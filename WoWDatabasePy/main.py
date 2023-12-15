import sqlite3
import requests
from pprint import pprint


api_key = "USMIEIzqNTCyRgGJLRKn7bbZO9gkP6A4NF"
realm = "illidan"
character_name = "melaraine"
target_key_count = 4  # Set the target number of completed keys
region = "us"
url = f"https://us.api.blizzard.com/profile/wow/character/{realm}/{character_name}/mythic-keystone-profile?namespace=profile-us&locale=en_US&access_token={api_key}"

response = requests.get(url)
data = response.json()

conn = sqlite3.connect('guild_database.db')


cursor = conn.cursor()


#create guild
cursor.execute('''
    CREATE TABLE IF NOT EXISTS guilds (
        guild_id INTEGER PRIMARY KEY,
        guild_name TEXT21
    )
''')
#create characters
cursor.execute('''
    CREATE TABLE IF NOT EXISTS characters (
        character_id INTEGER PRIMARY KEY,
        character_name TEXT,
        item_level INTEGER,
        guild_id INTEGER,
        FOREIGN KEY (guild_id) REFERENCES guilds(guild_id)
    )
''')
conn.commit()


def check_highest_keystone(api_key, region, realm, character_name):

    character_name = input("Enter Character Name: ").lower()
    print(f"Checking highest Mythic+ keystone for {character_name} on {realm}-{region}.")

    url = f"https://{region}.api.blizzard.com/profile/wow/character/{realm}/{character_name}/mythic-keystone-profile?namespace=profile-{region.lower()}&locale=en_US&access_token={api_key}"

    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error: Unable to fetch data. Status code: {response.status_code}")
        print(response.text)
        return

    data = response.json()




    if "current_mythic_rating" in data:
        rating = data["current_mythic_rating"]["rating"]
        print(f"{character_name}'s current Mythic+ rating is: {rating:.2f}")
    else:
        print(f"No Mythic Keystone data found for {character_name}")


def get_or_create_guild(cursor):
    guild_name = input("Enter the guild name: ")

    cursor.execute("SELECT guild_id FROM guilds WHERE guild_name = ?", (guild_name,))
    existing_guild = cursor.fetchone()

    if existing_guild:
        guild_id = existing_guild[0]
        print(f"Guild '{guild_name}' already exists.")
    else:
        cursor.execute("INSERT INTO guilds (guild_name) VALUES (?)", (guild_name,))
        conn.commit()
        guild_id = cursor.lastrowid
        print(f"Guild '{guild_name}' created successfully!")

    return guild_id


def create_character(cursor, guild_id):
    character_name = input("Enter character name: ")
    item_level = int(input("Enter character item level: "))
    cursor.execute("INSERT INTO characters (character_name, item_level, guild_id) VALUES (?, ?, ?)",
                   (character_name, item_level, guild_id))
    conn.commit()
    print(f"Character '{character_name}' added successfully!")


def display_characters_in_guild(cursor, guild_id):
    cursor.execute('''
        SELECT characters.character_id, characters.character_name
        FROM characters
        JOIN guilds ON characters.guild_id = guilds.guild_id
        WHERE guilds.guild_id = ?
    ''', (guild_id,))

    characters = cursor.fetchall()

    if not characters:
        print(f"No characters found in the guild '{guild_id}'.")
    else:
        print(f"Characters in the guild '{guild_id}':")
        for character in characters:
            print(f"ID: {character[0]}, Name: {character[1]}")


def remove_character(cursor, character_id):
    cursor.execute("DELETE FROM characters WHERE character_id = ?", (character_id,))
    conn.commit()
    print(f"Character with ID {character_id} has been removed.")


def display_all_guilds(cursor):
    cursor.execute("SELECT * FROM guilds")
    guilds = cursor.fetchall()

    if not guilds:
        print("No guilds found.")
    else:
        print("All Guilds:")
        for guild in guilds:
            print(f"ID: {guild[0]}, Name: {guild[1]}")


def clear_guild(cursor, guild_id):
    # Retrieve the guild name for display
    cursor.execute("SELECT guild_name FROM guilds WHERE guild_id = ?", (guild_id,))
    guild_name = cursor.fetchone()[0]

    # Clear the guild by deleting all characters
    cursor.execute("DELETE FROM characters WHERE guild_id = ?", (guild_id,))
    conn.commit()

    print(f"All characters in the guild '{guild_name}' (ID: {guild_id}) have been cleared.")


def delete_guild(cursor, guild_id):
    # Retrieve the guild name for display
    cursor.execute("SELECT guild_name FROM guilds WHERE guild_id = ?", (guild_id,))
    guild_name = cursor.fetchone()[0]

    # Delete the guild and all associated characters
    cursor.execute("DELETE FROM characters WHERE guild_id = ?", (guild_id,))
    cursor.execute("DELETE FROM guilds WHERE guild_id = ?", (guild_id,))
    conn.commit()

    print(f"Guild '{guild_name}' (ID: {guild_id}) and all its characters have been deleted.")

def display_characters_above_threshold(cursor, guild_id, threshold):
    cursor.execute('''
        SELECT character_id, character_name, item_level
        FROM characters
        WHERE guild_id = ? AND item_level > ?
    ''', (guild_id, threshold))

    characters_above_threshold = cursor.fetchall()

    if not characters_above_threshold:
        print(f"No characters found in the guild '{guild_id}' with item levels above {threshold}.")
    else:
        print(f"Characters in the guild '{guild_id}' with item levels above {threshold}:")
        for character in characters_above_threshold:
            print(f"ID: {character[0]}, Name: {character[1]}, Item Level: {character[2]}")
# Main loop
conn = sqlite3.connect('guild_database.db')
cursor = conn.cursor()
guild_id = None  # Initialize guild_id to None

while True:
    print("\nOptions:")
    print("1. Get or create a guild")
    print("2. Add characters to a guild")
    print("3. Access guild information")
    print("4. Display all created guilds")
    print("5. Clear the guild (delete all characters)")
    print("6. Remove a character from the guild")
    print("7. Delete a guild and all its characters")
    print("8. Check raider.io score")
    print("9. Exit")

    choice = input("Enter your choice (1-9): ")

    if choice == '1':
        guild_id = get_or_create_guild(cursor)
    elif choice == '2':
        if guild_id is None:
            print("Please get or create a guild first.")
        else:
            num_characters = int(input("Enter the number of characters you want to add: "))
            for _ in range(num_characters):
                create_character(cursor, guild_id)
    elif choice == '3' and guild_id is not None:
        print("\nGuild Information Options:")
        print("1. Display character names and IDs")
        print("2. Remove a character from the guild")
        print("3. Display all characters above a specified threshold")
        sub_choice = input("Enter your sub-choice (1-2): ")
        if sub_choice == '1':
            display_characters_in_guild(cursor, guild_id)
        elif sub_choice == '2':
            character_id = int(input("Enter the ID of the character to remove: "))
            remove_character(cursor, character_id)
        elif sub_choice == '3':
            threshold = int(input("Enter the item level threshold: "))
            display_characters_above_threshold(cursor, guild_id, threshold)
        else:
            print("Invalid sub-choice. Please enter either 1 - 3.")
    elif choice == '4':
        display_all_guilds(cursor)
    elif choice == '5' and guild_id is not None:
        clear_guild(cursor, guild_id)
    elif choice == '6' and guild_id is not None:
        character_id = int(input("Enter the ID of the character to remove: "))
        remove_character(cursor, character_id)
    elif choice == '7':
        guild_id_to_delete = int(input("Enter the ID of the guild to delete: "))
        delete_guild(cursor, guild_id_to_delete)
        # Reset current guild_id to None after deletion, have to change later
        guild_id = None
    elif choice == '8':
        check_highest_keystone(api_key, region, realm, character_name)
    elif choice == '9':
        break
    else:
        print("Invalid choice. Please enter a number between 1 and 8.")

conn.close()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
