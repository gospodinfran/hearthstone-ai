class Node:
    def __init__(self, data=None):
        self.data = data
        self.prev = None
        self.next = None
    
class DoublyLinkedList:
    def __init__(self, size=13):
        self.size = size
        self.nodes = [Node() for _ in range(size)]
        for i in range(size - 1):
            self.nodes[i].next = self.nodes[i + 1]
            self.nodes[i + 1].prev = self.nodes[i]
        self.head = self.nodes[0]
        self.tail = self.nodes[-1]
        self.middle = self.nodes[6]

    def display(self):
        curr = self.head
        print("[ ", end="")
        while curr:
            print(curr.data, end=" -> ")
            curr = curr.next
        print("]")
        
    def play_minion(self, minion, pos):
        if pos is None:
            self.middle.data = minion
        elif 0 <= pos < self.size and self.nodes[pos].data is None:
            self.nodes[pos].data = minion
        else:
            raise IndexError("Index out of range or position is empty.")
    
    def remove_minion(self, pos):
        if 0 <= pos < self.size:
            self.nodes[pos].data = None
        else:
            raise IndexError("Index out of range.")
