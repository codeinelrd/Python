# Book.py
class Book:
    headings = ['ID', 'Title', 'Author', 'Publication Year']
    fields = {
        '-ID-': 'Book ID:',
        '-Title-': 'Book Title:',
        '-Author-': 'Author:',
        '-PublicationYear-': 'Publication Year:'
    }

    def __init__(self, ID, title, author, publication_year):
        self.ID = ID
        self.title = title
        self.author = author
        self.publication_year = publication_year
        self.erased = False

    def __eq__(self, other_book):
        return other_book.ID == self.ID

    def __str__(self):
        return f"ID: {self.ID}\nTitle: {self.title}\nAuthor: {self.author}\nPublication Year: {self.publication_year}"

    def set_book(self, title, author, publication_year):
        self.title = title
        self.author = author
        self.publication_year = publication_year

