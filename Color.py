from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QPlainTextEdit, QHBoxLayout
)
import sys, webcolors


def get_color_name_and_family(hex_value):
    """Return the closest CSS3 name and general family (Red, Blue, Green, etc.).

    Always returns a 3-tuple: (name, family, rgb). On invalid input, name will be
    'Invalid' or 'Error' and rgb will be (0,0,0).
    """
    try:
        hex_value = (hex_value or "").strip().lstrip("#")
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
    except (ValueError, TypeError):
        # Parsing problems or unexpected types -> return an error sentinel
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
    """Generate an accessible textual description of the color."""
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
        # Input row with visible label (helps screen readers announce the field)
        input_row = QHBoxLayout()
        self.hex_label = QLabel("Hex color:")
        self.hex_label.setAccessibleName("Hex color label")
        self.hex_input = QLineEdit()
        self.hex_input.setAccessibleName("Color hex input")
        self.hex_input.setAccessibleDescription("Enter a six-digit hex color value such as #1E90FF.")
        self.hex_input.setPlaceholderText("Enter hex value (e.g. #1E90FF)")
        # Associate label with input for assistive tech
        self.hex_label.setBuddy(self.hex_input)
        input_row.addWidget(self.hex_label)
        input_row.addWidget(self.hex_input)

        # Action button; also allow Return/Enter in input to activate
        self.button = QPushButton("Describe Color")
        self.button.setAccessibleName("Describe Color button")
        self.button.setAccessibleDescription("Activates the color description and contrast check")
        self.button.clicked.connect(self.describe_color)
        self.hex_input.returnPressed.connect(self.button.click)

        # Use QPlainTextEdit for output so it's focusable, selectable, and fully readable
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setAccessibleName("Color description output")
        self.output.setAccessibleDescription("Shows the color name, family and an accessible description")
        self.output.setPlaceholderText("Color description will appear here")

        self.contrast_output = QPlainTextEdit()
        self.contrast_output.setReadOnly(True)
        self.contrast_output.setAccessibleName("Contrast checker output")
        self.contrast_output.setAccessibleDescription("Shows contrast ratios against black and white and recommendations")
        self.contrast_output.setPlaceholderText("Contrast information will appear here")

        # Arrange widgets
        self.layout.addLayout(input_row)
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.output)
        self.layout.addWidget(self.contrast_output)

        # Set a logical tab order for keyboard navigation
        self.setTabOrder(self.hex_input, self.button)
        self.setTabOrder(self.button, self.output)
        self.setTabOrder(self.output, self.contrast_output)

    def describe_color(self):
        hex_value = self.hex_input.text()
        name, family, rgb = get_color_name_and_family(hex_value)

        if name == "Invalid":
            self.output.setPlainText("Invalid hex value. Please enter a value like #1E90FF.")
            return

        description = describe_color(rgb, name, family)

        # Contrast ratios
        white = (255, 255, 255)
        black = (0, 0, 0)
        contrast_white = contrast_ratio(rgb, white)
        contrast_black = contrast_ratio(rgb, black)

        self.output.setPlainText(f"Color: {name}\nFamily: {family}\nDescription: {description}")
        self.output.setAccessibleDescription(description)

        contrast_text = (
            f"Contrast ratio vs white: {contrast_white}:1\n"
            f"Contrast ratio vs black: {contrast_black}:1"
        )
        if contrast_white < 4.5 and contrast_black < 4.5:
            contrast_text += "\nWarning: Low contrast on both white and black backgrounds."
        elif contrast_white >= 4.5:
            contrast_text += "\nBest viewed on a dark background."
        else:
            contrast_text += "\nBest viewed on a light background."

        self.contrast_output.setPlainText(contrast_text)
        self.contrast_output.setAccessibleDescription(contrast_text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ColorFinder()
    window.show()
    sys.exit(app.exec())
