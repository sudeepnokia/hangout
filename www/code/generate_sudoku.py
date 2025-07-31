import os
import random

def find_empty(board):
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == 0:
                return (i, j)
    return None

def is_valid(board, row, col, num):
    for i in range(9):
        if board[row][i] == num:
            return False

    for i in range(9):
        if board[i][col] == num:
            return False

    box_x = col // 3
    box_y = row // 3
    for i in range(box_y * 3, box_y * 3 + 3):
        for j in range(box_x * 3, box_x * 3 + 3):
            if board[i][j] == num:
                return False
    return True

def solve(board):
    find = find_empty(board)
    if not find:
        return True
    else:
        row, col = find

    nums = list(range(1, 10))
    random.shuffle(nums)

    for num in nums:
        if is_valid(board, row, col, num):
            board[row][col] = num
            if solve(board):
                return True
            board[row][col] = 0
    return False

def generate_puzzle(difficulty=1):
    board = [[0 for _ in range(9)] for _ in range(9)]
    solve(board)
    solution = [row[:] for row in board]
    
    squares = [(i, j) for i in range(9) for j in range(9)]
    random.shuffle(squares)
    
    # Adjust the number of removed cells based on difficulty
    if difficulty == 1: # Easy
        num_to_remove = 40
    elif difficulty == 2: # Medium
        num_to_remove = 50
    else: # Hard
        num_to_remove = 60

    for i in range(num_to_remove):
        row, col = squares[i]
        board[row][col] = 0
        
    return board, solution

def create_sudoku_html():
    puzzle, solved_puzzle = generate_puzzle()
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sudoku</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            flex-direction: column;
            background-color: #f4f4f4;
        }}
        h1 {{
            color: #333;
        }}
        #sudoku-board {{
            border: 3px solid #333;
            border-collapse: collapse;
            background-color: #fff;
        }}
        #sudoku-board td {{
            width: 40px;
            height: 40px;
            text-align: center;
            font-size: 20px;
            border: 1px solid #ccc;
        }}
        #sudoku-board td input {{
            width: 100%;
            height: 100%;
            border: none;
            text-align: center;
            font-size: 20px;
            padding: 0;
            box-sizing: border-box;
            color: #007bff;
        }}
        #sudoku-board td input:disabled {{
            background-color: #eee;
            color: #333;
            font-weight: bold;
        }}
        #sudoku-board tr:nth-child(3n) td,
        #sudoku-board tr:nth-child(6n) td {{
            border-bottom: 2px solid #333;
        }}
        #sudoku-board td:nth-child(3n),
        #sudoku-board td:nth-child(6n) {{
            border-right: 2px solid #333;
        }}
        .controls {{
            margin-top: 20px;
        }}
        button {{
            padding: 10px 20px;
            font-size: 16px;
            cursor: pointer;
            border: none;
            border-radius: 5px;
            background-color: #007bff;
            color: white;
            margin: 0 10px;
        }}
        button:hover {{
            background-color: #0056b3;
        }}
        #message {{
            margin-top: 15px;
            font-size: 18px;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <h1>Sudoku</h1>
    <table id="sudoku-board"></table>
    <div class="controls">
        <button id="new-game-btn">New Game</button>
        <button id="check-solution-btn">Check Solution</button>
    </div>
    <p id="message"></p>

    <script>
        const boardElement = document.getElementById('sudoku-board');
        const newGameBtn = document.getElementById('new-game-btn');
        const checkSolutionBtn = document.getElementById('check-solution-btn');
        const messageElement = document.getElementById('message');

        let solution = {str(solved_puzzle)};
        const puzzle = {str(puzzle)};

        function generateBoard() {{
            let board = JSON.parse(JSON.stringify(puzzle));
            boardElement.innerHTML = '';
            messageElement.textContent = '';

            for (let i = 0; i < 9; i++) {{
                const row = document.createElement('tr');
                for (let j = 0; j < 9; j++) {{
                    const cell = document.createElement('td');
                    const input = document.createElement('input');
                    input.setAttribute('type', 'number');
                    input.setAttribute('min', '1');
                    input.setAttribute('max', '9');
                    
                    if (board[i][j] !== 0) {{
                        input.value = board[i][j];
                        input.disabled = true;
                    }}
                    
                    input.dataset.row = i;
                    input.dataset.col = j;
                    cell.appendChild(input);
                    row.appendChild(cell);
                }}
                boardElement.appendChild(row);
            }}
        }}

        function checkSolution() {{
            const inputs = boardElement.getElementsByTagName('input');
            let isCorrect = true;
            let isComplete = true;

            for (const input of inputs) {{
                const row = input.dataset.row;
                const col = input.dataset.col;
                const value = parseInt(input.value, 10);

                if (!value) {{
                    isComplete = false;
                }}

                if (value !== solution[row][col]) {{
                    isCorrect = false;
                }}
            }}

            if (!isComplete) {{
                messageElement.textContent = "The board is not complete!";
                messageElement.style.color = "orange";
            }} else if (isCorrect) {{
                messageElement.textContent = "Congratulations! You solved it!";
                messageElement.style.color = "green";
            }} else {{
                messageElement.textContent = "Something is wrong. Keep trying!";
                messageElement.style.color = "red";
            }}
        }}

        newGameBtn.addEventListener('click', () => window.location.reload());
        checkSolutionBtn.addEventListener('click', checkSolution);

        // Initial game generation
        generateBoard();
    </script>
</body>
</html>
    """
    # The script will be in www/code, so we go one directory up to place the html file in www
    output_path = os.path.join(os.path.dirname(__file__), '../sudoku.html')
    try:
        with open(output_path, "w") as f:
            f.write(html_content)
        print(f"Successfully created sudoku.html in {{os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))}}")
    except Exception as e:
        print(f"An error occurred: {{e}}")

if __name__ == "__main__":
    create_sudoku_html()