from Book import Book

# CSV
import pandas as pd

def save_book_csv(csv_filename, book):
    # Create a Pandas DataFrame from the Book object
    book_data = {
        "ID": [book.ID],
        "title": [book.title],
        "author": [book.author],
        "publication_year": [book.publication_year],
        "erased": [book.erased]
    }
    df = pd.DataFrame(book_data)

    # 'a' mode to append at the end of the file if it already exists
    df.to_csv(csv_filename, mode='a', index=False, header=not pd.io.common.file_exists(csv_filename))

def modify_book_csv(csv_filename, book):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_filename)

    # Find the row that has the same ID as the book to be updated
    mask = df['ID'] == book.ID

    # If such a row is found, update the values of that row with the new values of the book
    df.loc[mask, ['ID', 'title', 'author', 'publication_year']] = [book.ID, book.title, book.author, book.publication_year]

    # Save the DataFrame back to the CSV file
    df.to_csv(csv_filename, index=False)

def read_book_csv(csv_filename):
    try:
        # Try to read the CSV file into a DataFrame
        df = pd.read_csv(csv_filename)
    except FileNotFoundError:
        # Print an error message if the file is not found
        print(f"Error: The file {csv_filename} was not found.")
        return []

    if df is None or df.empty:
        # Print a warning if the DataFrame is empty
        print("Warning: The DataFrame is empty.")
        return []

    # List that will store the Book objects
    book_list: list[Book] = []

    # Check if the required columns are present in the DataFrame
    required_columns = ['ID', 'title', 'author', 'publication_year', 'erase']
    if not all(column in df.columns for column in required_columns):
        print(f"Error: The required columns {required_columns} are not present in the DataFrame.")
        return []

    # Iterate over the rows of the DataFrame
    for index, row in df.iterrows():
        # Check if 'erase' is False and the required columns are present
        if 'erase' in row and row['erase'] == False:
            book_list.append(Book(row['ID'], row['title'], row['author'], row['publication_year']))

    return book_list

