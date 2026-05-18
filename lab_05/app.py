from pathlib import Path
import re
import urllib.request

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st


# -----------------------------
# Налаштування
# -----------------------------

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


# -----------------------------
# Завантаження та парсинг даних
# -----------------------------

def get_noaa_url(province_id: int) -> str:
    return (
        "https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/get_TS_admin.php?"
        f"country=UKR&provinceID={province_id}&year1={YEAR_START}&year2={YEAR_END}&type=Mean"
    )


def download_vhi_file(province_id: int) -> Path:
    file_path = RAW_DATA_DIR / f"province_{province_id:02d}.csv"

    if file_path.exists():
        return file_path

    url = get_noaa_url(province_id)

    with urllib.request.urlopen(url) as response:
        content = response.read().decode("utf-8", errors="ignore")

    file_path.write_text(content, encoding="utf-8")
    return file_path


def parse_vhi_file(file_path: Path, province_id: int) -> pd.DataFrame:
    """
    Надійний парсер NOAA-файлу.

    Він не залежить від HTML-розмітки, а просто шукає в рядках
    числові значення: year, week, SMN, SMT, VCI, TCI, VHI.
    """
    raw_text = file_path.read_text(encoding="utf-8", errors="ignore")

    rows = []
    for line in raw_text.splitlines():
        # Прибираємо HTML-теги, якщо вони є
        clean_line = re.sub(r"<[^>]+>", " ", line).strip()

        # Шукаємо числа в рядку
        numbers = re.findall(r"-?\d+(?:\.\d+)?", clean_line)

        if len(numbers) < 7:
            continue

        try:
            year = int(float(numbers[0]))
            week = int(float(numbers[1]))
        except ValueError:
            continue

        # Беремо лише реальні рядки даних
        if not (YEAR_START <= year <= YEAR_END and 1 <= week <= 52):
            continue

        try:
            row = [
                year,
                week,
                float(numbers[2]),
                float(numbers[3]),
                float(numbers[4]),
                float(numbers[5]),
                float(numbers[6]),
            ]
            rows.append(row)
        except ValueError:
            continue

    if not rows:
        raise ValueError(f"У файлі {file_path} не знайдено коректних рядків з даними.")

    df = pd.DataFrame(rows, columns=["year", "week", "SMN", "SMT", "VCI", "TCI", "VHI"])

    # Значення -1 часто означає пропуск
    df = df.replace(-1, np.nan)

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
        province_df = parse_vhi_file(file_path, province_id)
        frames.append(province_df)

    data = pd.concat(frames, ignore_index=True)

    numeric_columns = ["SMN", "SMT", "VCI", "TCI", "VHI"]

    for column in numeric_columns:
        data[column] = data.groupby("province_ua_index")[column].transform(
            lambda series: series.fillna(series.median())
        )

    data = data.sort_values(["province_ua_index", "year", "week"]).reset_index(drop=True)
    return data


# -----------------------------
# Фільтрація та графіки
# -----------------------------

def reset_filters() -> None:
    st.session_state["selected_index"] = "VCI"
    st.session_state["selected_region"] = "Вінницька"
    st.session_state["week_range"] = (1, 52)
    st.session_state["year_range"] = (YEAR_START, YEAR_END)
    st.session_state["sort_ascending"] = False
    st.session_state["sort_descending"] = False


def init_session_state() -> None:
    if "selected_index" not in st.session_state:
        st.session_state["selected_index"] = "VCI"

    if "selected_region" not in st.session_state:
        st.session_state["selected_region"] = "Вінницька"

    if "week_range" not in st.session_state:
        st.session_state["week_range"] = (1, 52)

    if "year_range" not in st.session_state:
        st.session_state["year_range"] = (YEAR_START, YEAR_END)

    if "sort_ascending" not in st.session_state:
        st.session_state["sort_ascending"] = False

    if "sort_descending" not in st.session_state:
        st.session_state["sort_descending"] = False


def apply_filters(
    data: pd.DataFrame,
    selected_index: str,
    selected_region: str,
    week_range: tuple[int, int],
    year_range: tuple[int, int],
    sort_ascending: bool,
    sort_descending: bool,
) -> pd.DataFrame:
    filtered = data[
        (data["province_ua_name"] == selected_region)
        & (data["week"].between(week_range[0], week_range[1]))
        & (data["year"].between(year_range[0], year_range[1]))
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

    plot_data = filtered.sort_values(["year", "week"]).copy()
    plot_data["period"] = (
        plot_data["year"].astype(str)
        + "-W"
        + plot_data["week"].astype(str).str.zfill(2)
    )

    ax.plot(range(len(plot_data)), plot_data[selected_index], linewidth=1.5)
    ax.set_title(f"{selected_index} для області: {selected_region}")
    ax.set_xlabel("Період")
    ax.set_ylabel(selected_index)
    ax.grid(True, alpha=0.3)

    if len(plot_data) > 20:
        tick_positions = np.linspace(0, len(plot_data) - 1, 10, dtype=int)
    else:
        tick_positions = np.arange(len(plot_data))

    ax.set_xticks(tick_positions)
    ax.set_xticklabels(plot_data.iloc[tick_positions]["period"], rotation=45, ha="right")
    fig.tight_layout()
    return fig


def plot_region_comparison(
    data: pd.DataFrame,
    selected_index: str,
    selected_region: str,
    week_range: tuple[int, int],
    year_range: tuple[int, int],
):
    comparison_data = data[
        (data["week"].between(week_range[0], week_range[1]))
        & (data["year"].between(year_range[0], year_range[1]))
    ].copy()

    grouped = (
        comparison_data.groupby("province_ua_name", as_index=False)[selected_index]
        .mean()
        .sort_values(selected_index, ascending=False)
    )

    fig, ax = plt.subplots(figsize=(12, 7))

    if grouped.empty:
        ax.text(0.5, 0.5, "Немає даних для порівняння", ha="center", va="center")
        ax.set_axis_off()
        return fig

    bars = ax.bar(grouped["province_ua_name"], grouped[selected_index])

    # Обрану область виділяємо штрихуванням
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


# -----------------------------
# Streamlit UI
# -----------------------------

st.set_page_config(
    page_title="Лабораторна №5 — VCI/TCI/VHI Dashboard",
    layout="wide",
)

st.title("Лабораторна робота №5")
st.subheader("Streamlit-додаток для аналізу VCI, TCI та VHI")

vhi_df = load_vhi_data()
init_session_state()

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
        value=st.session_state["week_range"],
        key="week_range",
    )

    year_range = st.slider(
        "Інтервал років",
        min_value=int(vhi_df["year"].min()),
        max_value=int(vhi_df["year"].max()),
        value=st.session_state["year_range"],
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
    data=vhi_df,
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
            data=vhi_df,
            selected_index=selected_index,
            selected_region=selected_region,
            week_range=week_range,
            year_range=year_range,
        )
        st.pyplot(fig_comparison)
