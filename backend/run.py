
from app import app, db

# Initialize the tables in the database
# with app.app_context():
#     db.create_all()

    
#TO ACTIVATE DEBUGG MODE
if __name__ == "__main__":
    app.run(debug=True) 