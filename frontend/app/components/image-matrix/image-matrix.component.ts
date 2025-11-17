import { Component, EventEmitter, Output } from '@angular/core';

interface Cell {
  imageFile?: File;
  imageUrl?: string;
  row: number;
  col: number;
}

@Component({
  selector: 'app-image-matrix',
  standalone: false,
  templateUrl: './image-matrix.component.html',
  styleUrls: ['./image-matrix.component.css']
})
export class ImageMatrixComponent {
  matrix: (Cell | undefined)[][] = [];
  lastAdded: Cell | null = null;
  historyStack: Cell[] = [];
  readonly rows = 2;
  readonly cols = 11;
  relations: string[] = [];

  @Output() imagesChange = new EventEmitter<File[]>();
  @Output() relationsChanged = new EventEmitter<string[]>();

  constructor() {
    this.addInitialCell();
  }

  private addInitialCell(): void {
    const centerCol = Math.floor(this.cols / 2);
    this.matrix = Array.from({ length: this.rows }, (_, row) =>
      Array.from({ length: this.cols }, (_, col) =>
        row === 0 && col === centerCol ? { row, col } : undefined
      )
    );
    this.lastAdded = this.matrix[0][centerCol]!;
    this.historyStack = [];
  }

  hasImages(): boolean {
    return this.historyStack.length > 0 || !!this.lastAdded?.imageFile;
  }

  get visibleRows(): number[] {
    const rowsSet = new Set<number>();
    for (const row of this.matrix) {
      for (const cell of row) {
        if ((cell?.imageFile || cell === this.lastAdded) && cell) rowsSet.add(cell.row);
      }
    }
    return Array.from(rowsSet).sort((a, b) => a - b);
  }

  get visibleCols(): number[] {
    const colsSet = new Set<number>();
    for (const row of this.matrix) {
      for (const cell of row) {
        if ((cell?.imageFile || cell === this.lastAdded) && cell) colsSet.add(cell.col);
      }
    }
    return Array.from(colsSet).sort((a, b) => a - b);
  }

  getCell(row: number, col: number): Cell | null {
    return this.matrix[row]?.[col] ?? null;
  }

  get cellWidth(): string {
    const count = this.visibleCols.length;
    const width = Math.max(300 - (count - 1) * 20, 120);
    return `${width}px`;
  }

  get cellHeight(): string {
    const widthNum = parseInt(this.cellWidth, 10);
    const height = Math.floor(widthNum * 0.6);
    return `${height}px`;
  }

  canAdd(direction: 'right' | 'left' | 'bottom' | 'top'): boolean {
    if (!this.lastAdded) return false;
    const { row, col } = this.lastAdded;

    switch (direction) {
      case 'left': return col > 0 && !this.matrix[row][col - 1];
      case 'right': return col < this.cols - 1 && !this.matrix[row][col + 1];
      case 'bottom': return row === 0 && !this.matrix[1][col];
      case 'top': return row === 1 && !this.matrix[0][col];
      default: return false;
    }
  }

  addImage(direction?: 'right' | 'left' | 'bottom' | 'top'): void {
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = 'image/*';

    fileInput.onchange = () => {
      const file = fileInput.files?.[0];
      if (!file) return;

      const imageUrl = URL.createObjectURL(file);

      if (direction) {
        this.placeImage(direction, file, imageUrl);
      } else if (this.lastAdded) {
        const { row, col } = this.lastAdded;
        const newCell: Cell = { row, col, imageFile: file, imageUrl };
        this.matrix[row][col] = newCell;
        this.lastAdded = newCell;
        this.historyStack.push(newCell);
        this.emitImages();
      }
    };

    fileInput.click();
  }

  private placeImage(direction: 'right' | 'left' | 'bottom' | 'top', file: File, imageUrl: string): void {
    if (!this.lastAdded) return;

    const { row, col } = this.lastAdded;
    let newRow = row;
    let newCol = col;

    if (direction === 'right') newCol++;
    else if (direction === 'left') newCol--;
    else if (direction === 'bottom') newRow++;
    else if (direction === 'top') newRow--;

    if (newRow < 0 || newRow >= this.rows || newCol < 0 || newCol >= this.cols) return;
    if (this.matrix[newRow][newCol]) return;

    const newCell: Cell = {
      row: newRow,
      col: newCol,
      imageFile: file,
      imageUrl
    };

    this.matrix[newRow][newCol] = newCell;
    this.lastAdded = newCell;
    this.historyStack.push(newCell);
    this.emitImages();

    const relation = this.computeRelation(direction, row);
    if (relation) {
      this.relations = [...this.relations, relation];
      console.log('Child: emitting relationsChange with:', this.relations);
      this.relationsChanged.emit(this.relations);
    }

    console.log('Relations:', this.relations);
  }


  deleteImage(row: number, col: number): void {
    if (!this.lastAdded || this.lastAdded.row !== row || this.lastAdded.col !== col) return;
    if (!this.matrix[row] || !this.matrix[row][col]) return;

    this.matrix[row][col] = undefined;

    this.historyStack = this.historyStack.filter(
      cell => !(cell.row === row && cell.col === col)
    );

    if (this.relations.length > 0) {
      this.relations = this.relations.slice(0, this.relations.length - 1);
      this.relationsChanged.emit(this.relations);
    }

    const centerCol = Math.floor(this.cols / 2);
    this.lastAdded = this.historyStack.length > 0
      ? this.historyStack[this.historyStack.length - 1]
      : this.matrix[0][centerCol] ?? null;

    this.emitImages();
  }

  private emitImages(): void {
    const files = this.historyStack
      .filter(cell => !!cell.imageFile)
      .map(cell => cell.imageFile!)
    this.imagesChange.emit(files);
  }

  private computeRelation(direction: 'right' | 'left' | 'bottom' | 'top', baseRow: number): string | null {
    if (baseRow === 0) {
      if (direction === 'right') return 'left-of';
      if (direction === 'left') return 'right-of';
      if (direction === 'bottom') return 'front-of';
    } else if (baseRow === 1) {
      if (direction === 'right') return 'right-of';
      if (direction === 'left') return 'left-of';
      if (direction === 'top') return 'front-of';
    }
    return null;
  }
}
