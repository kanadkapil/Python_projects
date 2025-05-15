import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Create a figure and axis
fig, ax = plt.subplots(figsize=(10, 6))
ax.axis('off')

# Define box properties
box_style = dict(boxstyle="round,pad=0.3", facecolor="lightblue", edgecolor="black")
arrow_style = dict(arrowstyle="->", color="black")

# Draw Java flow
ax.text(0.1, 0.9, "Java Source Code\n(.java)", bbox=box_style, ha="center")
ax.text(0.4, 0.9, "Java Compiler\n(javac)", bbox=box_style, ha="center")
ax.text(0.7, 0.9, "Bytecode\n(.class)", bbox=box_style, ha="center")
ax.text(0.9, 0.9, "JVM\n(Interpreter + JIT)", bbox=box_style, ha="center")
ax.annotate("", xy=(0.18, 0.9), xytext=(0.22, 0.9), arrowprops=arrow_style)
ax.annotate("", xy=(0.48, 0.9), xytext=(0.52, 0.9), arrowprops=arrow_style)
ax.annotate("", xy=(0.78, 0.9), xytext=(0.82, 0.9), arrowprops=arrow_style)

# Draw Python flow
ax.text(0.1, 0.5, "Python Source Code\n(.py)", bbox=box_style, ha="center")
ax.text(0.4, 0.5, "Python Interpreter\n(CPython)", bbox=box_style, ha="center")
ax.text(0.7, 0.5, "Bytecode\n(.pyc)", bbox=box_style, ha="center")
ax.text(0.9, 0.5, "Python Virtual Machine\n(PVM)", bbox=box_style, ha="center")
ax.annotate("", xy=(0.18, 0.5), xytext=(0.22, 0.5), arrowprops=arrow_style)
ax.annotate("", xy=(0.48, 0.5), xytext=(0.52, 0.5), arrowprops=arrow_style)
ax.annotate("", xy=(0.78, 0.5), xytext=(0.82, 0.5), arrowprops=arrow_style)

# Title
plt.title("Compilation and Interpretation Flow: Java vs Python", fontsize=14)

plt.show()
