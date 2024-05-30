import discord
import requests

# Define your API endpoint
API_URL = 'http://127.0.0.1:5000/chatbot'

# Specify the channel ID you want the bot to listen to
TARGET_CHANNEL_ID = 1244955866768212029  # Replace with your channel ID

# Initialize the bot with a command prefix
intents = discord.Intents.default()
intents.messages = True  # Ensure the bot can read messages
intents.message_content = True  # Ensure the bot can read message content
intents.guilds = True  # Ensure the bot can read guild information
client = discord.Client(intents=intents)

# Store the last message for repeating in case of an error
last_message = {}

# Store options to handle number-based responses
options_dict = {}

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    global last_message, options_dict
    # Check if the message is from the bot itself to prevent loops
    if message.author == client.user:
        return

    # Check if the message is in the target channel or in a thread in the target channel
    if message.channel.id != TARGET_CHANNEL_ID and (not isinstance(message.channel, discord.Thread) or message.channel.parent_id != TARGET_CHANNEL_ID):
        return

    # Check if the message content is empty
    if not message.content:
        print('Message content is empty or not text-based.')
        return

    # Check if the message is a number and if it corresponds to a stored option
    if message.content.isdigit() and message.channel.id in options_dict:
        option_number = int(message.content)
        print(message.content)
        if option_number == 0:
            selected_option = 'Back to Main Menu'
        elif 1 <= option_number <= len(options_dict[message.channel.id]):
            selected_option = options_dict[message.channel.id][option_number - 1]
        else:
            await message.channel.send("Invalid option. Please choose a valid option number.")
            return
    else:
        selected_option = message.content

    # Define the data to send in the API request
    data = {
        'choice': selected_option
    }

    # Send the data to the API
    response = requests.post(API_URL, json=data)

    # Log the API response to the console
    print(f'API Response: {response.status_code} - {response.text}')

    # Process the API response
    if response.status_code == 200:
        response_data = response.json()
        ## Nested response
        if "options" in response_data and "question" in response_data:
            print("Type 1 response data here",response_data["options"])
            response_data["options"].append("Back to Main Menu")

            # Type 1 response
            options = "\n".join([f"{i + 1}. {option}" for i, option in enumerate(response_data["options"])])
            print("options hereeee \n"+options)
            
            reply = f"{response_data['question']}\nOptions:\n{options}"
            if isinstance(message.channel, discord.Thread):
                # If the message is in a thread, respond in the same thread
                await message.channel.send(reply)
            else:
                # Create a thread if it doesn't exist
                thread = await message.channel.create_thread(name=f"{message.author.name}'s thread", message=message)
                await thread.send(reply)
                message.channel = thread
            last_message[message.channel.id] = reply
            options_dict[message.channel.id] = response_data["options"]
        elif "options" in response_data and response_data["options"] == ["Back to Main Menu"]:
            print("Type 2 response")
            # Type 2 response
            reply = f"{response_data['answer']}\nOptions:\n0. Back to Main Menu"
            if isinstance(message.channel, discord.Thread):
                # If the message is in a thread, respond in the same thread
                await message.channel.send(reply)
            else:
                # Create a thread if it doesn't exist
                thread = await message.channel.create_thread(name=f"{message.author.name}'s thread", message=message)
                await thread.send(reply)
                message.channel = thread
            last_message[message.channel.id] = reply
            options_dict[message.channel.id] = ["Back to Main Menu"]
        elif "error" in response_data:
            # Type 3 response
            if message.channel.id in last_message:
                await message.channel.send(last_message[message.channel.id])
            else:
                await message.channel.send(response_data["error"])
    else:
        # Handle non-200 responses or unexpected data formats
        await message.channel.send("An error occurred while processing your request. Please try again.")

# Run the bot with your token
client.run('MTI0NDYzNjAwMTIzNDU4MzU5Mg.GNLAVw.2LssQxoAxw3WDEG-riOjOgd9hpDi9NcmcJfbUg')
