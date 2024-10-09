import os
import streamlit as st
import pygame
import time
import random
import vertexai
from vertexai.generative_models import HarmCategory, HarmBlockThreshold
from vertexai.preview.generative_models import GenerativeModel

# Initialize Vertex AI with your credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "email-extraction-381718-3f73208ce3b71.json"
vertexai.init(project="email-extraction-381718", location="us-central1")
generative_multimodal_model = GenerativeModel("gemini-1.5-pro-001")

# Set up the display and the snake game settings
def generate_riddle():
    prompt = "Make funny coding related riddles to answer for candidates. I want them to be funny and interactive."

    generation_config = {
        "max_output_tokens": 8192,
        "temperature": 0.7,
        "top_p": 0.95,
    }
    safety_settings = {
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    }

    response = generative_multimodal_model.generate_content(prompt, generation_config=generation_config, safety_settings=safety_settings)
    return response.text

def ask_riddle():
    riddle = generate_riddle()
    st.write(f"Riddle: {riddle}")
    answer = st.text_input("Your Answer:")
    return riddle, answer

def snake_game():
    pygame.init()
    
    # Define the colors
    white = (255, 255, 255)
    yellow = (255, 255, 102)
    black = (0, 0, 0)
    red = (213, 50, 80)
    green = (0, 255, 0)
    blue = (50, 153, 213)
    
    # Screen width and height
    display_width = 600
    display_height = 400
    
    # Snake settings
    snake_block = 10
    snake_speed = 1
    
    # Set up the display
    display = pygame.display.set_mode((display_width, display_height))
    pygame.display.set_caption('Snake Riddle Game in Streamlit')
    
    # Clock to control snake speed
    clock = pygame.time.Clock()
    
    # Font styles
    font_style = pygame.font.SysFont(None, 30)
    
    def display_score(score):
        value = font_style.render("Your Score: " + str(score), True, yellow)
        display.blit(value, [0, 0])

    def draw_snake(snake_block, snake_list):
        for x in snake_list:
            pygame.draw.rect(display, green, [x[0], x[1], snake_block, snake_block])

    def display_message(msg, color):
        mesg = font_style.render(msg, True, color)
        display.blit(mesg, [display_width / 6, display_height / 3])

    def game_loop():
        game_over = False
        game_close = False
        
        # Initial position
        x1 = display_width / 2
        y1 = display_height / 2
        
        x1_change = 0
        y1_change = 0
        
        snake_list = []
        length_of_snake = 1
        
        # Movement control using riddles
        move_forward = True
        
        foodx = round(random.randrange(0, display_width - snake_block) / 10.0) * 10.0
        foody = round(random.randrange(0, display_height - snake_block) / 10.0) * 10.0
        
        while not game_over:
            
            while game_close:
                display.fill(black)
                display_message("You Lost! Press C-Continue or Q-Quit", red)
                display_score(length_of_snake - 1)
                pygame.display.update()
                
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_q:
                            game_over = True
                            game_close = False
                        if event.key == pygame.K_c:
                            game_loop()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
            
            display.fill(blue)
            
            # Riddle interaction and snake movement
            riddle, answer = ask_riddle()
            if riddle and answer:
                correct_answer = "correct"  # Replace this with actual logic to check the answer from model
                if answer.lower() == correct_answer:
                    x1_change = snake_block  # Move snake forward
                else:
                    x1_change = -snake_block  # Move snake backward
            
            x1 += x1_change
            display.fill(blue)
            
            # Draw the food and snake
            pygame.draw.rect(display, red, [foodx, foody, snake_block, snake_block])
            snake_head = [x1, y1]
            snake_list.append(snake_head)
            
            if len(snake_list) > length_of_snake:
                del snake_list[0]
            
            draw_snake(snake_block, snake_list)
            display_score(length_of_snake - 1)
            
            pygame.display.update()
            
            if x1 == foodx and y1 == foody:
                foodx = round(random.randrange(0, display_width - snake_block) / 10.0) * 10.0
                foody = round(random.randrange(0, display_height - snake_block) / 10.0) * 10.0
                length_of_snake += 1
            
            clock.tick(snake_speed)
        
        pygame.quit()
        quit()

    game_loop()

# Streamlit setup
st.title("Snake Riddle Game in Streamlit")
start_button = st.button("Start Snake Game")

if start_button:
    snake_game()
