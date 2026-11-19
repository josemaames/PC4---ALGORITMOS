"""
ESTRUCTURAS DE DATOS VISTAS EN CLASE (lab07 y lab09 del profesor)
Se copian tal cual para poder usarlas en la busqueda.
"""

# ---------------------------------------------------------------
# LAB 09 - COLA CIRCULAR (FIFO)
# ---------------------------------------------------------------
class myQueue:
    def __init__(self, cap):
        # ARREGLO PARA ALMACENAR LA COLA
        self.arr = [0]*cap
        # INDICE DEL ELEMENTO "FRONT"
        self.front = 0
        # NUMERO ACTUAL DE ELEMENTOS
        self.size = 0
        # CAPACIDAD MAXIMA
        self.capacity = cap

    def enqueue(self, x):
        if self.size == self.capacity:
            print("Queue is full!")
            return
        # AÑADE AL FINAL DE LA COLA
        rear = (self.front + self.size) % self.capacity
        self.arr[rear] = x
        self.size += 1

    def dequeue(self):
        if self.size == 0:
            print("Queue is empty!")
            return -1
        # SACAMOS EL ELEMENTO "FRONT"
        res = self.arr[self.front]
        # ACTUALIZAMOS EL INDICE "FRONT"
        self.front = (self.front + 1) % self.capacity
        self.size -= 1
        return res

    def getFront(self):
        if self.size == 0:
            return -1
        return self.arr[self.front]

    def getRear(self):
        if self.size == 0:
            return -1
        rear = (self.front + self.size - 1) % self.capacity
        return self.arr[rear]

    def isEmpty(self):
        return self.size == 0

    def isFull(self):
        return self.size == self.capacity

    def print_queue(self):
        arr2 = self.capacity*[0]
        for i in range(self.size):
            id = (self.front + i) % self.capacity
            arr2[i] = self.arr[id]
        print(arr2[0:self.size])


# ---------------------------------------------------------------
# LAB 09 - PILA (LIFO)
# ---------------------------------------------------------------
class myStack:
    def __init__(self, cap):
        self.capacity = cap
        self.arr = [0]*self.capacity
        self.top = -1

    def push(self, x):
        if self.top == self.capacity - 1:
            print("Stack Overflow")
            return
        self.top += 1
        self.arr[self.top] = x

    def pop(self):
        # LIFO
        if self.top == -1:
            print("Stack Underflow")
            return -1
        val = self.arr[self.top]
        self.top -= 1
        return val

    def peek(self):
        if self.top == -1:
            print("Stack is Empty")
            return -1
        return self.arr[self.top]

    def isEmpty(self):
        return self.top == -1

    def isFull(self):
        return self.top == self.capacity - 1

    def print_queue(self):
        print(self.arr[0:self.top+1])


# ---------------------------------------------------------------
# LAB 07 - MONTICULO MINIMO (ARREGLO)  [cola de prioridad propia]
# ---------------------------------------------------------------
class MinHeap:
    def __init__(self):
        self.arr = []

    def left(self, i):    # HIJO IZQUIERDO
        return 2*i + 1

    def right(self, i):   # HIJO DERECHO
        return 2*i + 2

    def parent(self, i):  # PADRE
        return (i - 1) // 2

    def get_min(self):
        return self.arr[0] if self.arr else None

    def insert(self, k):
        self.arr.append(k)
        i = len(self.arr) - 1
        # PROPAGAMOS EL NUEVO VALOR PARA ARRIBA
        while i > 0 and self.arr[self.parent(i)] > self.arr[i]:
            p = self.parent(i)
            self.arr[i], self.arr[p] = self.arr[p], self.arr[i]
            i = p

    def extract_min(self):
        if len(self.arr) <= 0:
            return None
        if len(self.arr) == 1:
            return self.arr.pop()
        res = self.arr[0]
        self.arr[0] = self.arr.pop()
        self.min_heapify(0)
        return res

    def min_heapify(self, i):
        # ARREGLAR EL HEAP PARA ABAJO
        n = len(self.arr)
        ind = i
        while True:
            l, r = self.left(ind), self.right(ind)
            smallest = ind
            if l < n and self.arr[l] < self.arr[smallest]:
                smallest = l
            if r < n and self.arr[r] < self.arr[smallest]:
                smallest = r
            if smallest == ind:
                break
            self.arr[ind], self.arr[smallest] = self.arr[smallest], self.arr[ind]
            ind = smallest

    def show_list(self):
        print(self.arr)


# TESTEO
if __name__ == '__main__':
    q = myQueue(5)
    for x in (10, 20, 30):
        q.enqueue(x)
    q.print_queue()
    print("dequeue:", q.dequeue())
    st = myStack(4)
    for x in (1, 2, 3):
        st.push(x)
    print("pop:", st.pop())
    h = MinHeap()
    for x in (5, 3, 8, 1):
        h.insert(x)
    h.show_list()
    print("min:", h.extract_min())
