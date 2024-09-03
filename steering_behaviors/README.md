# Obstacle Avoidance and Seek Behavior with Pygame

This project demonstrates a combination of obstacle avoidance and seek behavior using Pygame. The implemented `Mob` class allows an agent to navigate an environment filled with obstacles while following the mouse cursor. The code leverages vector mathematics to create realistic steering behaviors, making the agent avoid walls and other obstacles while seeking a target.

## Features
- **Obstacle Avoidance:** The agent detects nearby obstacles and adjusts its path to avoid collisions using predictive vectors.
- **Seek Behavior:** The agent follows the mouse cursor with a smooth approach, adjusting speed based on proximity.
- **Combined Behaviors:** Both avoidance and seeking are combined to enable complex navigation in dynamic environments.
- **Interactive Environment:** Click to add walls or remove them, and watch the agent dynamically adapt its path.

## Setup
To run this project, you'll need Python and Pygame installed. Clone the repository and run the script to see the behaviors in action.

## Inspiration 
This project was inspired by the Steering Behavior Examples from [kidscancode](https://github.com/kidscancode/pygame_tutorials/tree/master/examples/steering), which illustrates basic steering concepts in Pygame. Special thanks to [Chris Bradfield] for the foundational ideas!
