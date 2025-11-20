const SYMBOLS = [...'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'.split(''), '🍭', '🍬', '🍫', '🍡', '🍩', '🍪'];
const GRID_DIM = 3;
const MIN_SOLUTION_MOVES = 3;

// Status
let grid = [];
let selectedCell = null;
let verificationSuccess = false;
let winningCells = [];
let isAnimating = false;
let hasFiredVerify = false;
let animationCells = null;

// Hide and Lock cells
let hiddenCells = Array.from({ length: GRID_DIM }, () =>
    Array(GRID_DIM).fill(false)
);
let lockedCells = Array.from({ length: GRID_DIM }, () =>
    Array(GRID_DIM).fill(false)
);

// DOM
const gridContainer = document.getElementById('gridContainer');
const successMessage = document.getElementById('successMessage');
const refreshBtn = document.getElementById('refreshBtn');
let verificationSuccessCallback = null;

// Initialisation 
function initVerificationGame(callback) {
    verificationSuccessCallback = callback;
    refreshBtn.addEventListener('click', resetVerificationGame);
    resetVerificationGame();
}

// Reset
function resetVerificationGame() {
    grid = generateGridWithMinMoves(MIN_SOLUTION_MOVES);
    selectedCell = null;
    verificationSuccess = false;
    winningCells = [];
    isAnimating = false;
    hasFiredVerify = false;
    animationCells = null;
    randomizeHiddenAndLocked();

    successMessage.style.display = 'none';
    renderGrid();
}

// Randomly generate grids
function generateRandomGridNoLine() {
    while (true) {
        const grid = Array(GRID_DIM).fill().map(() =>
            Array(GRID_DIM).fill().map(() => SYMBOLS[Math.floor(Math.random() * SYMBOLS.length)])
        );
        if (!hasAnyLine(grid)) return grid;
    }
}

// check has any line
function hasAnyLine(grid) {
    // row
    for (let row of grid) {
        if (row[0] === row[1] && row[1] === row[2]) return true;
    }
    // column
    for (let col = 0; col < GRID_DIM; col++) {
        if (grid[0][col] === grid[1][col] && grid[1][col] === grid[2][col]) return true;
    }
    return false;
}

// fund winning lines
function findWinningLine(grid) {
    // row
    for (let r = 0; r < GRID_DIM; r++) {
        if (grid[r][0] === grid[r][1] && grid[r][1] === grid[r][2]) {
            return [[r, 0], [r, 1], [r, 2]];
        }
    }
    // column
    for (let c = 0; c < GRID_DIM; c++) {
        if (grid[0][c] === grid[1][c] && grid[1][c] === grid[2][c]) {
            return [[0, c], [1, c], [2, c]];
        }
    }
    return null;
}


// Vertical or Horizontal
function areAdjacent(cell1, cell2) {
    const [r1, c1] = cell1;
    const [r2, c2] = cell2;
    return (Math.abs(r1 - r2) + Math.abs(c1 - c2)) === 1;
}

// Shortest length（BFS）
function getShortestSolutionLength(grid, maxDepth = 5) {
    if (hasAnyLine(grid)) return 0;

    const start = grid.flat();
    const queue = [[start, 0]];
    const seen = new Set([start.join(',')]);

    const neighbors = [];
    for (let r = 0; r < GRID_DIM; r++) {
        for (let c = 0; c < GRID_DIM; c++) {
            const idx = r * GRID_DIM + c;
            if (r < GRID_DIM - 1) neighbors.push([idx, (r + 1) * GRID_DIM + c]);
            if (c < GRID_DIM - 1) neighbors.push([idx, r * GRID_DIM + (c + 1)]);
        }
    }

    while (queue.length > 0) {
        const [current, depth] = queue.shift();
        if (depth >= maxDepth) continue;

        for (const [i, j] of neighbors) {
            const next = [...current];
            [next[i], next[j]] = [next[j], next[i]];
            const key = next.join(',');

            if (seen.has(key)) continue;
            seen.add(key);

            const nextGrid = [];
            for (let r = 0; r < GRID_DIM; r++) {
                nextGrid.push(next.slice(r * GRID_DIM, (r + 1) * GRID_DIM));
            }

            if (hasAnyLine(nextGrid)) return depth + 1;
            queue.push([next, depth + 1]);
        }
    }

    return null;
}

function generateGridWithMinMoves(minMoves = 1) {
    const maxDepth = Math.max(minMoves, 4);
    while (true) {
        const grid = generateRandomGridNoLine();
        const steps = getShortestSolutionLength(grid, maxDepth);
        if (steps !== null && steps >= minMoves) {
            return grid;
        }
    }
}

// Hidden/clocked cells
function randomizeHiddenAndLocked() {
    for (let r = 0; r < GRID_DIM; r++) {
        for (let c = 0; c < GRID_DIM; c++) {
            hiddenCells[r][c] = false;
            lockedCells[r][c] = false;
        }
    }

    // Hide a random cell.
    // The numebr of hidden cells is random
    const hiddenCount = Math.floor(Math.random() * 2) + 1;
    for (let i = 0; i < hiddenCount; i++) {
        const r = Math.floor(Math.random() * GRID_DIM);
        const c = Math.floor(Math.random() * GRID_DIM);
        hiddenCells[r][c] = true;
    }

    // Lock one of the 9 cells 
    let lr, lc;
    while (true) {
        lr = Math.floor(Math.random() * GRID_DIM);
        lc = Math.floor(Math.random() * GRID_DIM);
        if (!hiddenCells[lr][lc]) break;
    }
    lockedCells[lr][lc] = true;
}

// After each swap, randomly rotate one row or one column
// function randomRotate(gridRef) {
//     if (Math.random() < 0.5) {
//         // 旋转一行（循环右移）
//         const r = Math.floor(Math.random() * GRID_DIM);
//         const row = gridRef[r];
//         gridRef[r] = [row[GRID_DIM - 1], ...row.slice(0, GRID_DIM - 1)];
//     } else {
//         // 旋转一列（循环下移）
//         const c = Math.floor(Math.random() * GRID_DIM);
//         const top = gridRef[GRID_DIM - 1][c];
//         for (let r = GRID_DIM - 1; r > 0; r--) {
//             gridRef[r][c] = gridRef[r - 1][c];
//         }
//         gridRef[0][c] = top;
//     }
// }

function renderGrid() {
    gridContainer.innerHTML = '';

    for (let rowIndex = 0; rowIndex < GRID_DIM; rowIndex++) {
        const rowElement = document.createElement('div');
        rowElement.className = 'grid-row';

        for (let colIndex = 0; colIndex < GRID_DIM; colIndex++) {
            const cellElement = createCellElement(rowIndex, colIndex);
            rowElement.appendChild(cellElement);
        }

        gridContainer.appendChild(rowElement);
    }
}

function createCellElement(rowIndex, colIndex) {
    const cellElement = document.createElement('div');
    const cellContent = document.createElement('div');
    cellContent.className = 'cell-content';

    let cellClasses = ['grid-cell'];

    if (hiddenCells[rowIndex][colIndex]) {
        cellClasses.push('hidden-cell');
        cellContent.textContent = '?';
    } else {
        const content = grid[rowIndex][colIndex];
        cellContent.textContent = content;
    }

    if (lockedCells[rowIndex][colIndex]) {
        cellClasses.push('locked-cell');
    }

    if (selectedCell &&
        selectedCell[0] === rowIndex &&
        selectedCell[1] === colIndex &&
        !animationCells) {
        cellClasses.push('selected');
    }

    if (winningCells.some(cell => cell[0] === rowIndex && cell[1] === colIndex)) {
        cellClasses.push('winning');
    }

    if (animationCells) {
        const { cell1, cell2, direction1, direction2 } = animationCells;
        const [r1, c1] = cell1;
        const [r2, c2] = cell2;

        if (rowIndex === r1 && colIndex === c1) {
            cellClasses.push('animating');
            cellElement.setAttribute('data-direction', direction1);
        } else if (rowIndex === r2 && colIndex === c2) {
            cellClasses.push('animating');
            cellElement.setAttribute('data-direction', direction2);
        }
    }

    cellElement.className = cellClasses.join(' ');

    cellElement.addEventListener('click', () => handleCellClick(rowIndex, colIndex));
    cellElement.addEventListener('mouseenter', () => handleCellMouseEnter(rowIndex, colIndex));
    cellElement.addEventListener('mouseleave', () => handleCellMouseLeave(rowIndex, colIndex));

    cellElement.appendChild(cellContent);
    return cellElement;
}

function handleCellClick(row, col) {
    if (verificationSuccess || isAnimating) return;

    if (lockedCells[row][col]) {
        return;
    }

    if (hiddenCells[row][col]) {
        hiddenCells[row][col] = false;
        renderGrid();
        return;
    }

    if (selectedCell === null) {
        selectedCell = [row, col];
        renderGrid();
    } else {
        const [r1, c1] = selectedCell;

        if (lockedCells[r1][c1]) {
            selectedCell = null;
            renderGrid();
            return;
        }

        if (r1 === row && c1 === col) {
            selectedCell = null;
            renderGrid();
            return;
        }

        if (areAdjacent([r1, c1], [row, col])) {
            isAnimating = true;

            refreshBtn.disabled = true;
            document.getElementById('closeBtn').disabled = true;

            let direction1, direction2;
            if (row > r1) {
                direction1 = 'down';
                direction2 = 'up';
            } else if (row < r1) {
                direction1 = 'up';
                direction2 = 'down';
            } else if (col > c1) {
                direction1 = 'right';
                direction2 = 'left';
            } else {
                direction1 = 'left';
                direction2 = 'right';
            }

            animationCells = {
                cell1: [r1, c1],
                cell2: [row, col],
                direction1,
                direction2
            };

            renderGrid();

            setTimeout(() => {

                [grid[r1][c1], grid[row][col]] = [grid[row][col], grid[r1][c1]];

                // randomRotate(grid);

                const winLine = findWinningLine(grid);
                if (winLine && !hasFiredVerify) {
                    hasFiredVerify = true;
                    winningCells = winLine;
                    verificationSuccess = true;
                    successMessage.style.display = 'block';

                    setTimeout(() => {
                        if (verificationSuccessCallback) {
                            verificationSuccessCallback();
                        }
                    }, 500);
                }

                animationCells = null;
                selectedCell = null;
                isAnimating = false;

                refreshBtn.disabled = false;
                document.getElementById('closeBtn').disabled = false;

                renderGrid();
            }, 300);

        } else {
            selectedCell = [row, col];
            renderGrid();
        }
    }
}

function handleCellMouseEnter(row, col) {
    if (isAnimating) return;

    const cellElement = getCellElement(row, col);
    if (!cellElement) return;

    if (
        hiddenCells[row][col] ||
        lockedCells[row][col] ||
        cellElement.classList.contains('selected') ||
        cellElement.classList.contains('winning')
    ) {
        return;
    }

    cellElement.classList.add('hovered');
}

function handleCellMouseLeave(row, col) {
    if (isAnimating) return;

    const cellElement = getCellElement(row, col);
    if (cellElement) {
        cellElement.classList.remove('hovered');
    }
}

function getCellElement(row, col) {
    const rows = gridContainer.querySelectorAll('.grid-row');
    if (rows[row]) {
        const cells = rows[row].querySelectorAll('.grid-cell');
        return cells[col];
    }
    return null;
}