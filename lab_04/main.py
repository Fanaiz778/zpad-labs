import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, CheckButtons
from scipy.signal import butter, filtfilt


class HarmonicNoiseApp:
    """Interactive app for harmonic signal with noise and filtering."""

    def __init__(self):
        self.default_amplitude = 1.0
        self.default_frequency = 1.0
        self.default_phase = 0.0
        self.default_noise_mean = 0.0
        self.default_noise_covariance = 0.2
        self.default_filter_cutoff = 3.0

        self.amplitude = self.default_amplitude
        self.frequency = self.default_frequency
        self.phase = self.default_phase
        self.noise_mean = self.default_noise_mean
        self.noise_covariance = self.default_noise_covariance
        self.filter_cutoff = self.default_filter_cutoff

        self.show_noise = True
        self.show_filtered = True

        self.x = np.linspace(0, 10, 1000)
        self.sample_rate = len(self.x) / (self.x[-1] - self.x[0])

        self.rng = np.random.default_rng(42)
        self.noise = self.generate_noise()

        self.fig, self.ax = plt.subplots(figsize=(12, 7))
        plt.subplots_adjust(left=0.12, bottom=0.42, right=0.82)

        self.clean_line, = self.ax.plot([], [], label="Чиста гармоніка", linewidth=2)
        self.noisy_line, = self.ax.plot([], [], label="Гармоніка з шумом", alpha=0.75)
        self.filtered_line, = self.ax.plot([], [], label="Відфільтрований сигнал", linewidth=2)

        self.ax.set_title("Гармоніка з шумом та фільтрацією")
        self.ax.set_xlabel("Час")
        self.ax.set_ylabel("Амплітуда")
        self.ax.grid(True, alpha=0.3)
        self.ax.legend(loc="upper right")

        self.create_widgets()
        self.update_plot()

    def harmonic_with_noise(
        self,
        amplitude: float,
        frequency: float,
        phase: float,
        noise_mean: float,
        noise_covariance: float,
        show_noise: bool,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Creates clean harmonic signal and harmonic signal with noise.

        Parameters:
        amplitude - amplitude of harmonic.
        frequency - frequency of harmonic.
        phase - phase shift.
        noise_mean - mean value of noise.
        noise_covariance - noise variance.
        show_noise - flag that controls whether noise is shown.
        """
        clean_signal = amplitude * np.sin(2 * np.pi * frequency * self.x + phase)

        if show_noise:
            noisy_signal = clean_signal + self.noise
        else:
            noisy_signal = clean_signal.copy()

        filtered_signal = self.filter_signal(noisy_signal)
        return clean_signal, noisy_signal, filtered_signal

    def generate_noise(self) -> np.ndarray:
        """Generates noise using current noise parameters."""
        std = np.sqrt(max(self.noise_covariance, 0.0001))
        return self.rng.normal(self.noise_mean, std, len(self.x))

    def filter_signal(self, signal: np.ndarray) -> np.ndarray:
        """Filters signal using Butterworth low-pass filter."""
        nyquist = 0.5 * self.sample_rate
        cutoff = min(self.filter_cutoff, nyquist - 0.1)
        normalized_cutoff = cutoff / nyquist
        b, a = butter(N=4, Wn=normalized_cutoff, btype="low")
        return filtfilt(b, a, signal)

    def create_widgets(self):
        """Creates sliders, checkboxes, and reset button."""
        slider_color = "lightgoldenrodyellow"

        ax_amplitude = plt.axes([0.12, 0.32, 0.62, 0.03], facecolor=slider_color)
        ax_frequency = plt.axes([0.12, 0.27, 0.62, 0.03], facecolor=slider_color)
        ax_phase = plt.axes([0.12, 0.22, 0.62, 0.03], facecolor=slider_color)
        ax_noise_mean = plt.axes([0.12, 0.17, 0.62, 0.03], facecolor=slider_color)
        ax_noise_covariance = plt.axes([0.12, 0.12, 0.62, 0.03], facecolor=slider_color)
        ax_filter_cutoff = plt.axes([0.12, 0.07, 0.62, 0.03], facecolor=slider_color)

        self.slider_amplitude = Slider(
            ax=ax_amplitude,
            label="Амплітуда",
            valmin=0.1,
            valmax=5.0,
            valinit=self.default_amplitude,
            valstep=0.1,
        )
        self.slider_frequency = Slider(
            ax=ax_frequency,
            label="Частота",
            valmin=0.1,
            valmax=5.0,
            valinit=self.default_frequency,
            valstep=0.1,
        )
        self.slider_phase = Slider(
            ax=ax_phase,
            label="Фаза",
            valmin=0.0,
            valmax=2 * np.pi,
            valinit=self.default_phase,
            valstep=0.1,
        )
        self.slider_noise_mean = Slider(
            ax=ax_noise_mean,
            label="Середнє шуму",
            valmin=-1.0,
            valmax=1.0,
            valinit=self.default_noise_mean,
            valstep=0.05,
        )
        self.slider_noise_covariance = Slider(
            ax=ax_noise_covariance,
            label="Дисперсія шуму",
            valmin=0.01,
            valmax=2.0,
            valinit=self.default_noise_covariance,
            valstep=0.01,
        )
        self.slider_filter_cutoff = Slider(
            ax=ax_filter_cutoff,
            label="Частота фільтра",
            valmin=0.2,
            valmax=10.0,
            valinit=self.default_filter_cutoff,
            valstep=0.1,
        )

        self.slider_amplitude.on_changed(self.on_harmonic_change)
        self.slider_frequency.on_changed(self.on_harmonic_change)
        self.slider_phase.on_changed(self.on_harmonic_change)
        self.slider_noise_mean.on_changed(self.on_noise_change)
        self.slider_noise_covariance.on_changed(self.on_noise_change)
        self.slider_filter_cutoff.on_changed(self.on_filter_change)

        ax_check = plt.axes([0.84, 0.70, 0.14, 0.12])
        self.check_buttons = CheckButtons(
            ax_check,
            ["Показати шум", "Показати фільтр"],
            [self.show_noise, self.show_filtered],
        )
        self.check_buttons.on_clicked(self.on_check_clicked)

        ax_reset = plt.axes([0.84, 0.60, 0.12, 0.05])
        self.reset_button = Button(ax_reset, "Reset")
        self.reset_button.on_clicked(self.reset)

        instruction_text = (
            "Інструкція:\\n"
            "1. Змінюйте амплітуду, частоту і фазу слайдерами.\\n"
            "2. Змінюйте середнє та дисперсію шуму.\\n"
            "3. Checkbox вмикає/вимикає шум і фільтр.\\n"
            "4. Reset повертає початкові параметри.\\n"
            "5. Якщо змінюються лише параметри гармоніки, шум не генерується заново.\\n"
            "6. Новий шум генерується лише після зміни параметрів шуму."
        )
        self.fig.text(0.84, 0.18, instruction_text, fontsize=8, va="bottom")

    def on_harmonic_change(self, _):
        """Updates harmonic parameters without regenerating noise."""
        self.amplitude = self.slider_amplitude.val
        self.frequency = self.slider_frequency.val
        self.phase = self.slider_phase.val
        self.update_plot()

    def on_noise_change(self, _):
        """Updates noise parameters and regenerates noise."""
        self.noise_mean = self.slider_noise_mean.val
        self.noise_covariance = self.slider_noise_covariance.val
        self.noise = self.generate_noise()
        self.update_plot()

    def on_filter_change(self, _):
        """Updates filter parameter without regenerating noise."""
        self.filter_cutoff = self.slider_filter_cutoff.val
        self.update_plot()

    def on_check_clicked(self, label):
        """Handles checkbox clicks."""
        if label == "Показати шум":
            self.show_noise = not self.show_noise
        elif label == "Показати фільтр":
            self.show_filtered = not self.show_filtered

        self.update_plot()

    def update_plot(self):
        """Updates all graph lines."""
        clean_signal, noisy_signal, filtered_signal = self.harmonic_with_noise(
            amplitude=self.amplitude,
            frequency=self.frequency,
            phase=self.phase,
            noise_mean=self.noise_mean,
            noise_covariance=self.noise_covariance,
            show_noise=self.show_noise,
        )

        self.clean_line.set_data(self.x, clean_signal)

        if self.show_noise:
            self.noisy_line.set_data(self.x, noisy_signal)
            self.noisy_line.set_visible(True)
        else:
            self.noisy_line.set_visible(False)

        if self.show_filtered:
            self.filtered_line.set_data(self.x, filtered_signal)
            self.filtered_line.set_visible(True)
        else:
            self.filtered_line.set_visible(False)

        y_min = min(clean_signal.min(), noisy_signal.min(), filtered_signal.min()) - 0.5
        y_max = max(clean_signal.max(), noisy_signal.max(), filtered_signal.max()) + 0.5
        self.ax.set_xlim(self.x.min(), self.x.max())
        self.ax.set_ylim(y_min, y_max)

        self.fig.canvas.draw_idle()

    def reset(self, _):
        """Resets all parameters to initial values."""
        self.slider_amplitude.reset()
        self.slider_frequency.reset()
        self.slider_phase.reset()
        self.slider_noise_mean.reset()
        self.slider_noise_covariance.reset()
        self.slider_filter_cutoff.reset()

        self.amplitude = self.default_amplitude
        self.frequency = self.default_frequency
        self.phase = self.default_phase
        self.noise_mean = self.default_noise_mean
        self.noise_covariance = self.default_noise_covariance
        self.filter_cutoff = self.default_filter_cutoff

        self.noise = self.generate_noise()
        self.update_plot()

    def run(self):
        plt.show()


if __name__ == "__main__":
    app = HarmonicNoiseApp()
    app.run()
