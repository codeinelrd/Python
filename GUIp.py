# Importaciones de módulos necesarios
from idlelib import window
import PySimpleGUI as sg
import re
import operator
import pandas as pd

from Book import Book
from SerializeFile import save_book_csv, read_book_csv

# List that will store the Book objects read from the CSV file
book_list = []

# Definition of regular expression patterns for validation
pattern_ID = r"\d{3}"
pattern_publication_year = r"\d{4}"

def purgeBooks(book_list, t_BookInterfaz):
    # Read the CSV file and store the data in a DataFrame
    df = pd.read_csv('Book.csv')

    # Delete rows that have 'erase' set to True
    df = df[df['erase'] != True]

    # Save the DataFrame back to the CSV file
    df.to_csv('Book.csv', index=False)

# Function to add a new book to the list and save the data in a CSV file.
def add_book(book_list, t_BookInterfaz, oBook, window):
    # Verify if the ID already exists
    if check_id_exists('Book.csv', oBook.ID):
        sg.popup_error('The ID already exists.')
        return

    # If no book with the same ID exists, proceed to add the new book
    save_book_csv('Book.csv', oBook)
    book_list.append(oBook)
    t_BookInterfaz.append([oBook.ID, oBook.title, oBook.author, oBook.publication_year])

    # Print statements for debugging
    print("Book added successfully:")
    print("ID:", oBook.ID)
    print("Title:", oBook.title)
    print("Author:", oBook.author)
    print("Publication Year:", oBook.publication_year)

    # Update the table in the GUI
    window['-Table-'].update(t_BookInterfaz)

# Function to remove a book from the list and update the interface and the CSV file.
def delBook(book_list, t_BookInterfaz, posinTable):
    # Read the CSV file and store the data in a DataFrame
    df = pd.read_csv('Book.csv')

    # Search for the row that has the same ID as the book to be deleted
    book_id = t_BookInterfaz[posinTable][0]
    mask = df['ID'] == book_id

    # If such row is found, set the 'erase' value to True
    df.loc[mask, 'erase'] = True

    # Save the DataFrame back to the CSV file
    df.to_csv('Book.csv', index=False)

    # Search for the book in the list and delete it
    for o in book_list:
        if o.ID == book_id:
            o.erased = True
            break

    # Delete the book from the interface list
    for i, book in enumerate(t_BookInterfaz):
        if book[0] == book_id:
            del t_BookInterfaz[i]
            break

def check_id_exists(csv_filename, id_to_check):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_filename)

    # Convert the ID column to string
    df['ID'] = df['ID'].astype(str)

    # Check if the ID exists in the ID column
    if str(id_to_check) in df['ID'].values:
        return True
    else:
        return False

# Function to update a book in the list and update the interface and the CSV file.
def updateBook(book_list, t_row_BookInterfaz):
    # Read the CSV file and store the data in a DataFrame
    df = pd.read_csv('Book.csv')

    # Get the ID of the book to be updated
    book_id = str(t_row_BookInterfaz[0])
    df['ID'] = df['ID'].astype(str)

    # Search for the row that has the same ID as the book to be updated
    mask = df['ID'] == book_id

    # If such row is found, update the values of the columns
    if df.loc[mask].shape[0] > 0:
        df.loc[mask, 'title'] = t_row_BookInterfaz[1]
        df.loc[mask, 'author'] = t_row_BookInterfaz[2]
        df.loc[mask, 'publication_year'] = t_row_BookInterfaz[3]

        # Save the DataFrame back to the CSV file
        df.to_csv('Book.csv', index=False)

        # Search for the book in the list and update it
        for o in book_list:
            if o.ID == book_id:
                o.set_book(t_row_BookInterfaz[1], t_row_BookInterfaz[2], t_row_BookInterfaz[3])
                o.erased = False  # Set the 'erased' value to False
                break
    else:
        print("Error: No se encontró un libro con el ID proporcionado.")

def handle_add_event(event, values, book_list, table_data, window):
    # Check if all fields have been filled
    if all([values['-ID-'], values['-Title-'], values['-Author-'], values['-PublicationYear-']]):
        # Additional validations if needed
        valida = True  # Assuming valida is True for simplicity, you can add your validations here

        if valida:
            # Add the new book to the list and update the interface
            new_book = Book(values['-ID-'], values['-Title-'], values['-Author-'], values['-PublicationYear-'])
            add_book(book_list, table_data, new_book, window)

            # Clear the input fields after adding a book
            window['-ID-'].update('')
            window['-Title-'].update('')
            window['-Author-'].update('')
            window['-PublicationYear-'].update('')

    else:
        # Show an error message if any of the fields is empty
        sg.popup_error('Todos los campos deben estar rellenados')

def handle_delete_event(event, values, book_list, table_data, window):
    if len(values['-Table-']) > 0:
        delBook(book_list, table_data, values['-Table-'][0])

        # Update the table in the GUI
        table_data.clear()
        for o in book_list:
            if not o.erased:
                table_data.append([o.ID, o.title, o.author, o.publication_year])

        # Update the table in the GUI
        window['-Table-'].update(table_data)

def handle_modify_event(event, values, book_list, table_data, window):
    valida = False
    if re.match(pattern_ID, values['-ID-']):
        if re.match(pattern_publication_year, values['-PublicationYear-']):
            valida = True
    if valida:
        rowToUpdate = None
        for t in table_data:
            if str(t[0]) == values['-ID-']:
                rowToUpdate = t
                t[1], t[2], t[3] = values['-Title-'], values['-Author-'], values['-PublicationYear-']
                break
        if rowToUpdate is None:
            print("Error: No se encontró un libro con el ID proporcionado EN EL EVENTO.")
            return
        updateBook(book_list, rowToUpdate)
        window['-Table-'].update(table_data)
        window['-ID-'].update(disabled=False)

# Function to read the data from the CSV file and store it in a list of Book objects.
def interfaz():
    # Definición de fuentes para la interfaz
    font1, font2 = ('Calibri', 16), ('Calibri', 18)

    # Configure the PySimpleGUI theme
    sg.theme('DarkBlue3')
    sg.set_options(font=font1)

    # List that will store the data to be displayed in the table
    table_data = []

    # List that will store the data of the row to be updated
    rowToUpdate = []

    # Read the CSV file and store the data in a list of Book objects
    book_list = read_book_csv('Book.csv')

    # Store the data of the Book objects in the list to be displayed in the table
    for o in book_list:
        table_data.append([o.ID, o.title, o.author, o.publication_year])

    # Definition of the layout of the GUI
    color_principal = '#02483e'  # Color principal (fondo)
    color_secundario = '#057c46'  # Color secundario (destacados)
    color_texto = '#9bb61b'  # Color del texto

    # Definition of the layout of the GUI
    layout = [
        [
            sg.Column([
                [sg.Text('ID:                        ', font=('Calibri', 16), text_color=color_texto, background_color=color_principal),
                 sg.Input(key='-ID-', font=('Calibri', 16), background_color=color_secundario)],
                [sg.Text('Title:                    ', font=('Calibri', 16), text_color=color_texto, background_color=color_principal),
                 sg.Input(key='-Title-', font=('Calibri', 16), background_color=color_secundario)],
                [sg.Text('Author:                ', font=('Calibri', 16), text_color=color_texto, background_color=color_principal),
                 sg.Input(key='-Author-', font=('Calibri', 16), background_color=color_secundario)],
                [sg.Text('Publication Year:', font=('Calibri', 16), text_color=color_texto,
                         background_color=color_principal),
                 sg.Input(key='-PublicationYear-', font=('Calibri', 16), background_color=color_secundario)],
                [sg.Push(background_color=color_principal)] +
                [sg.Button(button, button_color=(color_texto, color_secundario)) for button in
                 ('Add', 'Delete', 'Modify', 'Clear')] +
                [sg.Push(background_color=color_principal)],
                [sg.Button('Purge', button_color=(color_texto, color_secundario)), sg.Push(),
                 sg.Button('Sort File', button_color=(color_texto, color_secundario))],
            ], element_justification='l', expand_x=True, background_color=color_principal),
            # Alinea los elementos de la columna a la izquierda y expande en el eje X
            sg.Column([
                [sg.Table(values=table_data, headings=Book.headings,  col_widths=[1, 16, 14, 10], num_rows=20,
                          display_row_numbers=False, justification='right', enable_events=True,
                          enable_click_events=True, vertical_scroll_only=False,
                          select_mode=sg.TABLE_SELECT_MODE_BROWSE, expand_x=True, bind_return_key=True,
                          key='-Table-', auto_size_columns=False, background_color=color_principal)],
                # Alinea la tabla a la derecha
            ], element_justification='r', expand_x=True, background_color=color_principal)
            # Alinea los elementos de la columna a la derecha y expande en el eje X
        ]
    ]
    # Configura el tamaño de la ventana
    window_size = (1300, 500)  # Cambia estos valores según tus preferencias
    sg.theme('DarkGreen5')
    # Crea la ventana
    window = sg.Window('Book Management with CSV', layout, finalize=True, size=window_size)

    window['-Table-'].bind("<Double-Button-1>", " Double")

    # Event loop. Read buttons, make callbacks
    while True:
        event, values = window.read()

        # Manage the window closing event
        if event == sg.WIN_CLOSED:
            break

        # Manage the event of adding a new book
        if event == 'Add':
            handle_add_event(event, values, book_list, table_data, window)

        # Manage the event of deleting a book
        if event == 'Delete':
            handle_delete_event(event, values, book_list, table_data, window)

        # Manage the event of double clicking on a row in the table
        if event == '-Table- Double':
            if len(values['-Table-']) > 0:
                row = values['-Table-'][0]
                window['-ID-'].update(disabled=True)
                window['-ID-'].update(str(table_data[row][0]))
                window['-Title-'].update(str(table_data[row][1]))
                window['-Author-'].update(str(table_data[row][2]))
                window['-PublicationYear-'].update(str(table_data[row][3]))

        # Manage the event of clearing the fields
        if event == 'Clear':
            window['-ID-'].update(disabled=False)
            window['-ID-'].update('')
            window['-Title-'].update('')
            window['-Author-'].update('')
            window['-PublicationYear-'].update('')

        # Manage the event of modifying a book
        if event == 'Modify':
            handle_modify_event(event, values, book_list, table_data, window)

        # Manage the event of sorting the file
        if event == 'Sort File':
            # New window to select the value to sort by
            layout = ([[sg.Text('Select a value to sort by')],
                       [sg.Combo(['ID', 'title', 'author', 'publication_year'], key='-COMBO-', default_value='publication_year')],
                       [sg.Button('OK')]])
            sort_window = sg.Window('Sort File', layout)

            while True:  # Event Loop
                sort_event, sort_values = sort_window.read()
                if sort_event == 'OK':
                    sort_window.close()

                    df = pd.read_csv('Book.csv')

                    # Order the DataFrame by the selected value
                    df.sort_values(by=sort_values['-COMBO-'], inplace=True)

                    # Write the sorted DataFrame back to the CSV file
                    df.to_csv('Book.csv', index=False)
                    break
                elif sort_event == sg.WIN_CLOSED:
                    break
                else:
                    break

        # Manage the event of purging the file
        if event == 'Purge':
            purgeBooks(book_list, table_data)
            window['-Table-'].update(table_data)

    # close the window
    window.close()

# call the function
interfaz()