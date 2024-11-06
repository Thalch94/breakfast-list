from flask import Flask, render_template, request, redirect, url_for, jsonify
import pickle
import os

# Initialize Flask app
app = Flask(__name__)

app.config['ENV'] = 'production'
# File path to store pickled data internally
DATA_FILE = "name_list_data.pickle"

# Default Data
def get_default_data():
    breakfast_names = [
        "KDTN", "NIPS", "ADFK", "JHRN", "MSRG", "TSAK", "ARGN", "PYGP", 
        "ERKP", "MALA", "JAHP", "THSM", "MSGD", "OLLU", "KAGP", "YUKI", 
        "FVRA", "SYNO", "MARA", "CLKT", "ELPI", "PSKH"
    ]
    breakfast_click_counts = {name: 0 for name in breakfast_names}
    cleanup_names = breakfast_names.copy()
    cleanup_click_counts = {name: 0 for name in cleanup_names}
    return breakfast_names, breakfast_click_counts, cleanup_names, cleanup_click_counts

# Function to load names and click counts from the file or embedded pickled data
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "rb") as file:
                data = pickle.load(file)
                return data.get("breakfast_names", []), data.get("breakfast_click_counts", {}), data.get("cleanup_names", []), data.get("cleanup_click_counts", {})
        except Exception as e:
            print(f"Error loading data from file: {e}")
            return get_default_data()
    else:
        return get_default_data()

# Function to save names and click counts to the file
def save_data(breakfast_names, breakfast_click_counts, cleanup_names, cleanup_click_counts):
    data = {
        "breakfast_names": breakfast_names,
        "breakfast_click_counts": breakfast_click_counts,
        "cleanup_names": cleanup_names,
        "cleanup_click_counts": cleanup_click_counts
    }
    try:
        with open(DATA_FILE, "wb") as file:
            pickle.dump(data, file)
    except Exception as e:
        print(f"Error saving data: {e}")

# Initialize the data
breakfast_names, breakfast_click_counts, cleanup_names, cleanup_click_counts = load_data()

# Route for displaying the breakfast and cleanup lists
@app.route('/')
def index():
    return render_template('index.html', 
                           breakfast_names=breakfast_names, 
                           breakfast_click_counts=breakfast_click_counts, 
                           cleanup_names=cleanup_names, 
                           cleanup_click_counts=cleanup_click_counts)

# Route for adding a new name to both lists
@app.route('/add_name', methods=['POST'])
def add_name():
    new_name = request.form['name'].strip().upper()
    if new_name and new_name not in breakfast_names and new_name not in cleanup_names:
        breakfast_names.insert(0, new_name)
        cleanup_names.insert(0, new_name)
        breakfast_click_counts[new_name] = 0
        cleanup_click_counts[new_name] = 0
        save_data(breakfast_names, breakfast_click_counts, cleanup_names, cleanup_click_counts)
    return redirect(url_for('index'))

# Route for moving a name to the bottom of the list and incrementing the counter
@app.route('/move_to_bottom', methods=['POST'])
def move_to_bottom():
    name = request.form['name']
    table_type = request.form['table_type']
    
    if table_type == "breakfast" and name in breakfast_names:
        breakfast_click_counts[name] += 1
        breakfast_names.remove(name)
        breakfast_names.append(name)
    elif table_type == "cleanup" and name in cleanup_names:
        cleanup_click_counts[name] += 1
        cleanup_names.remove(name)
        cleanup_names.append(name)

    save_data(breakfast_names, breakfast_click_counts, cleanup_names, cleanup_click_counts)
    return redirect(url_for('index'))

# Route for deleting a name from both lists
@app.route('/delete_name', methods=['POST'])
def delete_name():
    name = request.form['name']
    if name in breakfast_names:
        breakfast_names.remove(name)
        del breakfast_click_counts[name]
    if name in cleanup_names:
        cleanup_names.remove(name)
        del cleanup_click_counts[name]
    
    save_data(breakfast_names, breakfast_click_counts, cleanup_names, cleanup_click_counts)
    return redirect(url_for('index'))

# Route for resetting all click counts for a table
@app.route('/reset_counts', methods=['POST'])
def reset_counts():
    table_type = request.form['table_type']
    
    if table_type == "breakfast":
        for name in breakfast_click_counts:
            breakfast_click_counts[name] = 0
    elif table_type == "cleanup":
        for name in cleanup_click_counts:
            cleanup_click_counts[name] = 0
    
    save_data(breakfast_names, breakfast_click_counts, cleanup_names, cleanup_click_counts)
    return redirect(url_for('index'))

# Run the app
if __name__ == '__main__':
   app.run(host="0.0.0.0", port=7153)