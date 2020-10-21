from IPython.display import clear_output, display, HTML, Javascript
from typing import List
import json

def handle_input(match: List[int]) -> str:
    for jdx in range(len(match)):
        if match[jdx] == 0:
            match[jdx] = -1
            return str(jdx)
    return str(-1)

player_fn = handle_input

js = """
class Match {
    constructor(identifier) {
        this.grid = Array(9).fill(0)
        this.gridDom = this.grid.map((_, idx) => {
            const cell = document.createElement('div')
            cell.className = 'ttt-cell'
            cell.innerText = '-'
            cell.onclick = () => this.handleClick(idx)
            return cell
        })
        this.container = document.getElementById(identifier)
        for (const cell of this.gridDom) {
            this.container.appendChild(cell)
        }
    }
    
    get side() {
        return Math.sqrt(this.grid.length)
    }
    
    reset = () => {
        for (const idx in this.grid) {
            this.grid[idx] = 0
            this.gridDom[idx].innerText = '-'
        }
    }
    
    restartGame = () => {
        alert('Game over!')
        this.reset()
    }
    
    handleClick = (idx) => {
        if (this.grid[idx] !== 0) return alert('Cell already used!')
        this.grid[idx] = 1
        this.gridDom[idx].innerText = 'X'
        const over = this.checkWin()
        if (over) return
        executePython(`player_fn(${JSON.stringify(this.grid)})`).then((jdx) => {
            if (jdx === '-1') return this.restartGame()
            this.grid[jdx] = -1
            this.gridDom[jdx].innerText = 'O'
            return new Promise((resolve) => setTimeout(resolve, 100))
        }).then(() => {
            this.checkWin()
        })
    }
    
    checkGroup = (group) => {
        const sum = group.reduce((a, v) => a + v, 0)
        return Math.floor(Math.abs(sum) / group.length) * Math.sign(sum)
    }
    
    
    checkWin = () => {
        // check rows
        for (let idx = 0; idx < this.side; idx++) {
            const row = this.grid.slice(idx * this.side, idx * this.side + this.side)
            const winner = this.checkGroup(row)
            if (Math.abs(winner) === 0) continue
            alert(`${winner === 1 ? 'X' : 'O'} is the winner!`)
            this.restartGame()
            return true
        }
        return false
    }
}

function executePython(python) {
    return new Promise(resolve => {
        const cb = {
            iopub: {
                output: data => {
                
                    resolve(data.content.text.trim())
                }
            }
        }
        Jupyter.notebook.kernel.execute(`print(${python})`, cb)
    })
}

new Match('grid')
"""

def play_game(handler=handle_input):
    global player_fn
    player_fn = handler
    display(HTML("""
    <style>
        #grid {
            display: flex;
            flex-wrap: wrap;
            flex-direction: row;
        }
        .ttt-cell {
            width: 33%;
        }

    </style>
    """))
    display(HTML(f"<div id='grid'></div>"))
    display(Javascript(js))