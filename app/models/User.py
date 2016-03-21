from system.core.model import Model
from flask import session

class User(Model):
    def __init__(self):
        super(User, self).__init__()

    def get_all_users(self):
        print self.db.query_db("SELECT * FROM users")

    def register_user(self, info):
        print "registering user"
        pw_hash = self.bcrypt.generate_password_hash(info['password'])
        register_info = [info['name'], info['alias'], info['email'], pw_hash]
        register_query = "INSERT INTO users (name, alias, email, pw_hash, created_at) VALUES (%s, %s, %s, %s, NOW())"
        return self.db.query_db(register_query, register_info)


    def validate_login(self, info):
        print "validating user info"
        email = info['email']
        errors = []
        try:
            verify_hash_query = "SELECT id, email, pw_hash FROM users WHERE email = %s"
            verify_hash_data = [email]
            query_return = self.db.query_db(verify_hash_query, verify_hash_data)
            password = info['password']
            if email == query_return[0]['email']:
                print "emails match"
                if self.bcrypt.check_password_hash(query_return[0]['pw_hash'], password):
                    print "passed pw validation"
                    session['id'] = query_return[0]['id']
                    return {"status" : True}
                else:
                    print "failed pw validation"
                    errors.append('incorrect password.')
                    return {"status": False, "errors" : errors}
        except:
            print "bad email."
            errors.append('bad email address.')
            return {"status": False, "errors": errors}

    def books_page_get(self):
        user_id = session['id']
        books_query = "SELECT * FROM reviews LEFT JOIN books ON books.id = reviews.book_id LEFT JOIN authors ON authors.id = books.author_id LIMIT 10"
        books_return = self.db.query_db(books_query)
        user_query = "SELECT name, alias, id FROM users WHERE id = %s"
        user_data = [user_id]
        user_return = self.db.query_db(user_query, user_data)
        print "retrieved successfully"
        return  books_return, user_return

    def authors_get(self):
        authors_query = "SELECT id, author_name FROM authors ORDER BY id DESC"
        authors_return = self.db.query_db(authors_query)
        return authors_return

    def book_check(self, data, authorfromlist):
        if authorfromlist:
            book_insert_query = "INSERT INTO books (title, author_id) VALUES (%s, %s)"
            book_insert_data = [data['title'], data['author_id']]
            book_insert_return = self.db.query_db(book_insert_query, book_insert_data)
            return {"status": True, "book": book_insert_return}
        else:
            author_insert_query = "INSERT INTO authors (author_name) VALUES (%s)"
            author_insert_data = [data['author_name']]
            author_insert_return = self.db.query_db(author_insert_query, author_insert_data)
            book_insert_query = "INSERT INTO books (title, author_id) VALUES (%s, %s)"
            book_insert_data = [data['title'], data['author_id']]
            book_insert_return = self.db.query_db(book_insert_query, book_insert_data)
            return {"status": True, "author": author_insert_return, "book": book_insert_return}

    def new_book_get(self):
        newest_book_query = "SELECT books.id FROM books ORDER BY books.id DESC LIMIT 1"
        newest_book = self.db.query_db(newest_book_query)[0]
        print "newest book", newest_book
        return newest_book

    def add_review(self, data):
        review_insert_query = "INSERT INTO reviews (book_id, content, posted_by, rating, created_at) VALUES (%s, %s, %s, %s, NOW())"
        review_insert_data = [data['book_id'], data['review_content'], data['posted_by'], data['rating']]
        review_return = self.db.query_db(review_insert_query, review_insert_data)
        print review_return
        return review_return
