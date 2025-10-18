from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QTextEdit
)
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt
import sys, webcolors, math


def get_color_name_and_family(hex_value):
    """Return the closest CSS3 color name, general color family, and RGB tuple."""
    try:
        hex_value = hex_value.strip().lstrip("#")
        if len(hex_value) != 6:
            return "Invalid", "Unknown", (0, 0, 0)

        rgb = tuple(int(hex_value[i:i + 2], 16) for i in (0, 2, 4))
        try:
            name = webcolors.rgb_to_name(rgb, spec="css3")
        except ValueError:
            name = "Unnamed color"

        r, g, b = rgb
        if r > g and r > b:
            family = "Red family"
        elif g > r and g > b:
            family = "Green family"
        elif b > r and b > g:
            family = "Blue family"
        elif r == g == b:
            family = "Gray tone"
        else:
            family = "Mixed hue"

        return name, family, rgb
    except Exception:
        return "Error", "Unknown", (0, 0, 0)


def relative_luminance(r, g, b):
    """Calculate luminance for WCAG contrast ratio."""
    def f(v):
        v = v / 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def contrast_ratio(fore_rgb, back_rgb):
    """Compute contrast ratio between two colors."""
    L1 = relative_luminance(*fore_rgb)
    L2 = relative_luminance(*back_rgb)
    lighter = max(L1, L2)
    darker = min(L1, L2)
    return round((lighter + 0.05) / (darker + 0.05), 2)


def describe_color(rgb, name, family):
    """Generate a plain-language description for nonvisual understanding."""
    r, g, b = rgb
    brightness = (r + g + b) / 3
    if brightness < 85:
        lightness_desc = "dark"
    elif brightness < 170:
        lightness_desc = "medium"
    else:
        lightness_desc = "light"

    temp_desc = "cool" if family in ("Blue family", "Green family", "Gray tone") else "warm"

    description = (
        f"{name} is a {lightness_desc} {temp_desc} color from the {family}. "
        f"Its brightness is about {int(brightness/2.55)} percent toward white."
    )
    return description


class ColorFinder(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Accessible Color and Contrast Checker")
        self.layout = QVBoxLayout(self)

        # Input field
        self.hex_input = QLineEdit()
        self.hex_input.setAccessibleName("Color hex input")
        self.hex_input.setAccessibleDescription(
            "Enter a six-digit hex color value such as #1E90FF."
        )
        self.hex_input.setPlaceholderText("Enter hex value (e.g. #1E90FF)")

        # Action button
        self.button = QPushButton("Describe Color")
        self.button.setAccessibleName("Describe Color button")
        self.button.setAccessibleDescription(
            "Press this button to analyze and describe the entered color."
        )
        self.button.clicked.connect(self.describe_color)

        # Output text areas (read-only QTextEdit for full screen reader navigation)
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setAccessibleName("Color description output")
        self.output.setAccessibleDescription(
            "Displays the color name, family, and detailed explanation."
        )
        self.output.setFocusPolicy(Qt.StrongFocus)
        self.output.setFrameStyle(QTextEdit.NoFrame)
        self.output.setTextInteractionFlags(
            Qt.TextSelectableByKeyboard | Qt.TextSelectableByMouse
        )

        self.contrast_output = QTextEdit()
        self.contrast_output.setReadOnly(True)
        self.contrast_output.setAccessibleName("Contrast checker output")
        self.contrast_output.setAccessibleDescription(
            "Displays contrast ratios against black and white backgrounds, with accessibility advice."
        )
        self.contrast_output.setFocusPolicy(Qt.StrongFocus)
        self.contrast_output.setFrameStyle(QTextEdit.NoFrame)
        self.contrast_output.setTextInteractionFlags(
            Qt.TextSelectableByKeyboard | Qt.TextSelectableByMouse
        )

        # Layout
        self.layout.addWidget(self.hex_input)
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.output)
        self.layout.addWidget(self.contrast_output)

    def describe_color(self):
        hex_value = self.hex_input.text()
        name, family, rgb = get_color_name_and_family(hex_value)

        if name == "Invalid":
            self.output.setText("Invalid hex value. Please enter a value like #1E90FF.")
            self.contrast_output.clear()
            return

        description = describe_color(rgb, name, family)

        # Contrast ratios
        white = (255, 255, 255)
        black = (0, 0, 0)
        contrast_white = contrast_ratio(rgb, white)
        contrast_black = contrast_ratio(rgb, black)

        # Descriptive outputs
        main_text = (
            f"Color: {name}\n"
            f"Family: {family}\n"
            f"Description: {description}\n"
            f"RGB values: {rgb}"
        )
        self.output.setText(main_text)

        contrast_text = (
            f"Contrast ratio vs white background: {contrast_white}:1\n"
            f"Contrast ratio vs black background: {contrast_black}:1\n"
        )

        if contrast_white < 4.5 and contrast_black < 4.5:
            contrast_text += (
                "Warning: This color has low contrast on both white and black backgrounds.\n"
            )
        else:
            # If contrast with white is higher, the color is dark → use light background.
            # If contrast with black is higher, the color is light → use dark background.
            if contrast_white > contrast_black:
                contrast_text += "Best viewed on a light background.\n"
            else:
                contrast_text += "Best viewed on a dark background.\n"

        # WCAG guidance
        if max(contrast_white, contrast_black) >= 7:
            contrast_text += "Meets WCAG AAA contrast for normal text."
        elif max(contrast_white, contrast_black) >= 4.5:
            contrast_text += "Meets WCAG AA contrast for normal text."
        elif max(contrast_white, contrast_black) >= 3:
            contrast_text += "Meets WCAG AA contrast for large text only."
        else:
            contrast_text += "Fails all WCAG contrast levels for text."

        self.contrast_output.setText(contrast_text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ColorFinder()
    window.show()
    sys.exit(app.exec())
