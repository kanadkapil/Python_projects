import matplotlib.pyplot as plt
from wordcloud import WordCloud
import os
import re

def parse_color_input(color_input):
    """Parse hex or RGB string into a format WordCloud can accept."""
    color_input = color_input.strip()

    if not color_input:
        return 'black'

    # Hex color: allow with or without #
    if re.fullmatch(r'#?[0-9A-Fa-f]{6}', color_input):
        return color_input if color_input.startswith('#') else f'#{color_input}'

    # RGB format: "255,255,255"
    if re.fullmatch(r'\d{1,3},\d{1,3},\d{1,3}', color_input):
        try:
            r, g, b = map(int, color_input.split(','))
            if all(0 <= val <= 255 for val in (r, g, b)):
                return (r, g, b)
        except ValueError:
            pass

    print("⚠️ Invalid color input. Using default: black")
    return 'black'

def generate_wallpaper(text, width=1920, height=1080, bg_color='black',
                       colormap='viridis', output_file='wallpaper.png',
                       max_words=200, scale=1.5):
    wordcloud = WordCloud(
        width=width,
        height=height,
        background_color=bg_color,
        colormap=colormap,
        max_words=max_words,
        scale=scale,
        collocations=False
    ).generate(text)

    wordcloud.to_file(output_file)
    print(f"✅ Wallpaper saved as '{output_file}'")

    plt.figure(figsize=(16, 9))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.title("Your Generated Word Cloud Wallpaper", fontsize=16)
    plt.show()

if __name__ == '__main__':
    print("\n🎨 Word Cloud Wallpaper Generator 🎨\n")

    # Text input choice
    print("How would you like to provide the text?")
    print("1. Type the text")
    print("2. Load from a text file")
    choice = input("Enter '1' or '2': ").strip()

    user_text = ""
    if choice == '1':
        user_text = input("✏️ Enter your text: ").strip()
    elif choice == '2':
        file_path = input("📄 Enter the full path to your text file: ").strip()
        if not os.path.exists(file_path):
            print("❌ File not found. Please check the path and try again.")
            exit()
        with open(file_path, 'r', encoding='utf-8') as f:
            user_text = f.read().strip() # Added strip() here
    else:
        print("❌ Invalid choice. Please run the program again.")
        exit()

    # Add a check for empty or whitespace-only text input
    if not user_text or not user_text.strip():
        print("❌ No valid text provided. Please enter some text to generate a word cloud.")
        exit()


    # Orientation input
    orientation = input("\n🖼️ Choose orientation - type 'horizontal' or 'vertical' (default: horizontal): ").strip().lower() or 'horizontal'

    if orientation == 'vertical':
        default_width, default_height = 1080, 1920
    else:
        default_width, default_height = 1920, 1080

    # Resolution input
    print(f"\n📏 Enter resolution (in pixels). Press Enter to use default {default_width}x{default_height}.")
    width_input = input("Width: ").strip()
    height_input = input("Height: ").strip()

    width = int(width_input) if width_input.isdigit() else default_width
    height = int(height_input) if height_input.isdigit() else default_height

    # Background color input
    print("\n🎨 Background color:")
    print("- Enter hex (e.g., #000000 or FFFFFF)")
    print("- Or RGB (e.g., 255,255,255)")
    bg_input = input("Background color (default: black): ")
    bg_color = parse_color_input(bg_input)

    # Colormap
    colormap = input("🌈 Color map (e.g., viridis, plasma, cool, spring - default: viridis): ").strip() or 'viridis'

    # Text density
    print("\n🔠 Choose text density (how dense the word cloud appears):")
    print("Options: light, normal, high, very high (default: normal)")
    density_input = input("Density: ").strip().lower() or 'normal'

    density_settings = {
        'light': {'max_words': 100, 'scale': 1.0},
        'normal': {'max_words': 200, 'scale': 1.5},
        'high': {'max_words': 400, 'scale': 2.0},
        'very high': {'max_words': 800, 'scale': 2.5},
    }

    if density_input not in density_settings:
        print("⚠️ Invalid density choice. Using default: normal")
        density_input = 'normal'

    max_words = density_settings[density_input]['max_words']
    scale = density_settings[density_input]['scale']

    # Generate and display
    print("\n⏳ Generating your wallpaper...\n")
    generate_wallpaper(user_text, width=width, height=height,
                       bg_color=bg_color, colormap=colormap,
                       max_words=max_words, scale=scale)
