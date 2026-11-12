# =====================================================================
# Topic: Extraction of Class and Caste Dynamics using LLM
# Author Name(s): Manisha Low
# Short Description: This file contains extracted thematic textual 
# evidence from Tagore's "The Child's Return" focusing on class divide, 
# along with a script to visualize the frequency of these themes.
# Semester: Monsoon Semester 2026
# Affiliation: Student
# =====================================================================

import matplotlib.pyplot as plt

# Extracted themes based on the LLM prompt
thematic_extractions = {
    "Master-Servant Dynamics": [
        "Raicharan was twelve years old when he came as a servant to his master's house.",
        "But when a mistress came into the house, Raicharan found two masters instead of one.",
        "His mistress ordered him out of the house.",
        "Anukul's magisterial conscience would not allow him... 'No,' he said, 'he cannot be forgiven for what he has done.'"
    ],
    "Economic Disparity": [
        "He bought him also a yellow satin waistcoat, a gold-laced cap, and some gold bracelets and anklets.",
        "The money that Raicharan had brought with him from the sale of his land was exhausted.",
        "He had been starving himself for the boy's sake, so he had grown physically weak...",
        "The boy was continually grumbling about his clothes and asking for more money."
    ],
    "Subaltern Sacrifice": [
        "He melted down the ornaments of his dead wife and made gold bangles and anklets.",
        "He spared no pains to give him the best education, the best clothes, the best food.",
        "Meanwhile, he himself lived on a mere handful of rice...",
        "It was not the Padma that stole your baby. It was I."
    ]
}

def visualize_themes():
    # Prepare data for plotting
    categories = list(thematic_extractions.keys())
    counts = [len(thematic_extractions[cat]) for cat in categories]

    # Create a bar chart
    plt.figure(figsize=(9, 6))
    bars = plt.bar(categories, counts, color=['#4C72B0', '#55A868', '#C44E52'], edgecolor='black')
    
    # Customization
    plt.title("Manifestation of Class & Subaltern Exploitation\nin 'The Child's Return'", fontsize=14, fontweight='bold')
    plt.xlabel("Analytical Themes (Marxist/Subaltern Framework)", fontsize=12)
    plt.ylabel("Number of Textual Instances Extracted", fontsize=12)
    plt.ylim(0, max(counts) + 1)
    
    # Add value labels on top of bars
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 0.1, int(yval), ha='center', va='bottom', fontsize=11)

    # Show plot
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    visualize_themes()