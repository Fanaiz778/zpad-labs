from pathlib import Path
from io import StringIO
import re
import urllib.request

import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt


RAW_DATA_DIR = Path("data/raw/vhi")
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

YEAR_START = 1981
YEAR_END = 2024

NOAA_PROVINCES = {
    1: "Cherkasy",
    2: "Chernihiv",
    3: "Chernivtsi",
    4: "Crimea",
    5: "Dnipropetrovsk",
    6: "Donetsk",
    7: "Ivano-Frankivsk",
    8: "Kharkiv",
    9: "Kherson",
    10: "Khmelnytskyi",
    11: "Kyiv Oblast",
    12: "Kyiv City",
    13: "Kirovohrad",
    14: "Luhansk",
    15: "Lviv",
    16: "Mykolaiv",
    17: "Odesa",
    18: "Poltava",
    19: "Rivne",
    20: "Sevastopol",
    21: "Sumy",
    22: "Ternopil",
    23: "Zakarpattia",
    24: "Vinnytsia",
    25: "Volyn",
    26: "Zaporizhzhia",
    27: "Zhytomyr",
}

UKRAINIAN_REGION_INDEX = {
    24: (1, "Вінницька"),
    25: (2, "Волинська"),
    5: (3, "Дніпропетровська"),
    6: (4, "Донецька"),
    27: (5, "Житомирська"),
    23: (6, "Закарпатська"),
    26: (7, "Запорізька"),
    7: (8, "Івано-Франківська"),
    11: (9, "Київська"),
    13: (10, "Кіровоградська"),
    14: (11, "Луганська"),
    15: (12, "Львівська"),
    16: (13, "Миколаївська"),
    17: (14, "Одеська"),
    18: (15, "Полтавська"),
    19: (16, "Рівненська"),
    21: (17, "Сумська"),
    22: (18, "Тернопільська"),
    8: (19, "Харківська"),
    9: (20, "Херсонська"),
    10: (21, "Хмельницька"),
    1: (22, "Черкаська"),
    3: (23, "Чернівецька"),
    2: (24, "Чернігівська"),
    4: (25, "АР Крим"),
    12: (26, "м. Київ"),
    20: (27, "м. Севастополь"),
}


def get_noaa_url(province_id: int, year_start: int = YEAR_START, year_end: int = YEAR_END) -> str:
    return (
        "https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/get_TS_admin.php?"
        f"country=UKR&provinceID={province_id}&year1={year_start}&year2={year_end}&type=Mean"
    )


def download_vhi_file(province_id: int) -> Path:
    existing_files = sorted(RAW_DATA_DIR.glob(f"province_{province_id:02d}.csv"))
    if existing_files:
        return existing_files[-1]

    file_path = RAW_DATA_DIR / f"province_{province_id:02d}.csv"
    url = get_noaa_url(province_id)

    with urllib.request.urlopen(url) as response:
        content = response.read().decode("utf-8", errors="ignore")

    file_path.write_text(content, encoding="utf-8")
    return file_path


def parse_vhi_file(file_path: Path, province_id: int) -> pd.DataFrame:
    raw_text = file_path.read_text(encoding="utf-8", errors="ignore")
    clean_text = re.sub(r"<[^>]+>", "", raw_text)
    lines = clean_text.splitlines()

    data_lines = []
    for line in lines:
        line = line.strip()
        if re.match(r"^\d{4}\s*,", line):
            data_lines.append(line)

    if not data_lines:
        raise ValueError(f"У файлі {file_path} не знайдено рядків з даними.")

    csv_text = "year,week,SMN,SMT,VCI,TCI,VHI\n" + "\n".join(data_lines)
    df = pd.read_csv(StringIO(csv_text))

    for column in df.columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df = df.replace(-1, np.nan)
    df = df.dropna(subset=["year", "week"])

    df["year"] = df["year"].astype(int)
    df["week"] = df["week"].astype(int)

    ua_index, ua_name = UKRAINIAN_REGION_INDEX[province_id]
    df["province_noaa_id"] = province_id
    df["province_noaa_name"] = NOAA_PROVINCES[province_id]
    df["province_ua_index"] = ua_index
    df["province_ua_name"] = ua_name

    return df


@st.cache_data(show_spinner="Завантаження та підготовка VCI/TCI/VHI даних...")
def load_vhi_data() -> pd.DataFrame:
    frames = []

    for province_id in NOAA_PROVINCES:
        file_path = download_vhi_file(province_id)
        frames.append(parse_vhi_file(file_path, province_id))

    df = pd.concat(frames, ignore_index=True)

    numeric_columns = ["SMN", "SMT", "VCI", "TCI", "VHI"]
    for column in numeric_columns:
        df[column] = df.groupby("province_ua_index")[column].transform(
            lambda series: series.fillna(series.median())
        )

    df = df.sort_values(["province_ua_index", "year", "week"]).reset_index(drop=True)
    return df


def reset_filters():
    st.session_state["selected_index"] = "VCI"
    st.session_state["selected_region"] = "Вінницька"
    st.session_state["week_range"] = (1, 52)
    st.session_state["year_range"] = (YEAR_START, YEAR_END)
    st.session_state["sort_ascending"] = False
    st.session_state["sort_descending"] = False


def apply_filters(
    df: pd.DataFrame,
    selected_index: str,
    selected_region: str,
    week_range: tuple[int, int],
    year_range: tuple[int, int],
    sort_ascending: bool,
    sort_descending: bool,
) -> pd.DataFrame:
    filtered = df[
        (df["province_ua_name"] == selected_region)
        & (df["week"].between(week_range[0], week_range[1]))
        & (df["year"].between(year_range[0], year_range[1]))
    ].copy()

    if sort_ascending and not sort_descending:
        filtered = filtered.sort_values(selected_index, ascending=True)
    elif sort_descending and not sort_ascending:
        filtered = filtered.sort_values(selected_index, ascending=False)
    elif sort_ascending and sort_descending:
        st.warning("Увімкнено обидва типи сортування. Дані залишено без сортування.")

    return filtered.reset_index(drop=True)


def plot_filtered_data(filtered: pd.DataFrame, selected_index: str, selected_region: str):
    fig, ax = plt.subplots(figsize=(12, 6))

    if filtered.empty:
        ax.text(0.5, 0.5, "Немає даних для обраних фільтрів", ha="center", va="center")
        ax.set_axis_off()
        return fig

    plot_df = filtered.sort_values(["year", "week"]).copy()
    plot_df["period"] = plot_df["year"].astype(str) + "-W" + plot_df["week"].astype(str).str.zfill(2)

    ax.plot(range(len(plot_df)), plot_df[selected_index], linewidth=1.5)
    ax.set_title(f"{selected_index} для області: {selected_region}")
    ax.set_xlabel("Період")
    ax.set_ylabel(selected_index)
    ax.grid(True, alpha=0.3)

    if len(plot_df) > 20:
        tick_positions = np.linspace(0, len(plot_df) - 1, 10, dtype=int)
    else:
        tick_positions = np.arange(len(plot_df))

    ax.set_xticks(tick_positions)
    ax.set_xticklabels(plot_df.iloc[tick_positions]["period"], rotation=45, ha="right")
    fig.tight_layout()
    return fig


def plot_region_comparison(
    df: pd.DataFrame,
    selected_index: str,
    selected_region: str,
    week_range: tuple[int, int],
    year_range: tuple[int, int],
):
    comparison_df = df[
        (df["week"].between(week_range[0], week_range[1]))
        & (df["year"].between(year_range[0], year_range[1]))
    ].copy()

    grouped = (
        comparison_df.groupby("province_ua_name", as_index=False)[selected_index]
        .mean()
        .sort_values(selected_index, ascending=False)
    )

    fig, ax = plt.subplots(figsize=(12, 7))

    if grouped.empty:
        ax.text(0.5, 0.5, "Немає даних для порівняння", ha="center", va="center")
        ax.set_axis_off()
        return fig

    bars = ax.bar(grouped["province_ua_name"], grouped[selected_index])

    for bar, region in zip(bars, grouped["province_ua_name"]):
        if region == selected_region:
            bar.set_hatch("//")
            bar.set_linewidth(2)

    ax.set_title(f"Порівняння середнього {selected_index} між областями")
    ax.set_xlabel("Область")
    ax.set_ylabel(f"Середнє значення {selected_index}")
    ax.tick_params(axis="x", rotation=75)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    return fig


st.set_page_config(
    page_title="Лабораторна №5 — VCI/TCI/VHI Dashboard",
    layout="wide",
)

st.title("Лабораторна робота №5")
st.subheader("Streamlit-додаток для аналізу VCI, TCI та VHI")

vhi_df = load_vhi_data()

if "selected_index" not in st.session_state:
    reset_filters()

regions = (
    vhi_df[["province_ua_index", "province_ua_name"]]
    .drop_duplicates()
    .sort_values("province_ua_index")["province_ua_name"]
    .tolist()
)

left_column, right_column = st.columns([1, 3])

with left_column:
    st.header("Фільтри")

    selected_index = st.selectbox(
        "Оберіть часовий ряд",
        options=["VCI", "TCI", "VHI"],
        key="selected_index",
    )

    selected_region = st.selectbox(
        "Оберіть область",
        options=regions,
        key="selected_region",
    )

    week_range = st.slider(
        "Інтервал тижнів",
        min_value=1,
        max_value=52,
        key="week_range",
    )

    year_range = st.slider(
        "Інтервал років",
        min_value=int(vhi_df["year"].min()),
        max_value=int(vhi_df["year"].max()),
        key="year_range",
    )

    sort_ascending = st.checkbox(
        f"Сортувати {selected_index} за зростанням",
        key="sort_ascending",
    )

    sort_descending = st.checkbox(
        f"Сортувати {selected_index} за спаданням",
        key="sort_descending",
    )

    st.button("Скинути фільтри", on_click=reset_filters)

    st.markdown("---")
    st.markdown(
        """
        **Пояснення:**  
        - вкладка **Таблиця** показує відфільтровані дані;  
        - вкладка **Графік** показує часовий ряд для обраної області;  
        - вкладка **Порівняння областей** показує середні значення по всіх областях.
        """
    )

filtered_df = apply_filters(
    df=vhi_df,
    selected_index=selected_index,
    selected_region=selected_region,
    week_range=week_range,
    year_range=year_range,
    sort_ascending=sort_ascending,
    sort_descending=sort_descending,
)

with right_column:
    tab_table, tab_plot, tab_comparison = st.tabs(
        ["Таблиця", "Графік", "Порівняння областей"]
    )

    with tab_table:
        st.subheader("Відфільтровані дані")
        st.write(f"Кількість записів: **{len(filtered_df)}**")
        st.dataframe(
            filtered_df[
                [
                    "province_ua_index",
                    "province_ua_name",
                    "year",
                    "week",
                    "VCI",
                    "TCI",
                    "VHI",
                ]
            ],
            use_container_width=True,
        )

    with tab_plot:
        st.subheader(f"Часовий ряд {selected_index}")
        fig_filtered = plot_filtered_data(filtered_df, selected_index, selected_region)
        st.pyplot(fig_filtered)

    with tab_comparison:
        st.subheader(f"Порівняння {selected_index} між областями")
        fig_comparison = plot_region_comparison(
            vhi_df,
            selected_index,
            selected_region,
            week_range,
            year_range,
        )
        st.pyplot(fig_comparison)
