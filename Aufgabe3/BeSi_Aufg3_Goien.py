import graphviz as gv
class ANDNODE:
    def __init__(self,name):
        self.name = name
        self.nodes = []
        
    def add(self,node):
        self.nodes.append(node)
        
    def draw(self):
        graph = gv.Graph()
        self.add_node(graph)
        graph.render('result.gv', view = True)
        
    def add_node(self, graph):
        graph.node(self.name, self.name + '\n(&)')
        for node in self.nodes:
            graph.edge(self.name, node.name)
            node.add_node(graph)
    
    def availability(self):
        product = 1
        for i in self.nodes:
            product *= (1-i.availability()) # U = Produkte der Nichtverfügbarkeiten
        self.avail = 1 - product # V = 1 - U
        return self.avail
    
class ORNODE:
    def __init__(self,name):
        self.name = name
        self.nodes = []
        
    def __repr__(self):
        return self.name
        
    def add(self,node):
        self.nodes.append(node)
        
    def draw(self):
        graph = gv.Graph()
        self.add_node(graph)
        graph.render('result.gv', view = True)
        
    def add_node(self, graph):
        graph.node(self.name, self.name + '\n(<=1)')
        for node in self.nodes:
            graph.edge(self.name, node.name)
            node.add_node(graph)
    
class EVENT:
    def __init__(self,name,la,mu):
        self.name = name
        self.la = la
        self.mu = mu
        
    def __repr__(self):
        return self.name
        
    def add_node(self,graph):
        graph.node(self.name, self.name)
        
    def nonavailability(self):
        self.nonavail = self.la / (self.la + self.mu) # U = lambda/(lambda+mü)
        return self.nonavail
    
    def availability(self):
        self.avail = 1 - self.nonavailability() 
        return self.avail

    def availability(self):
        product = 1
        for i in self.nodes:
            product *= i.availability() # V = Produkte der Verfügbarkeiten
        self.avail = product
        return self.avail

class NODE:
    def __init__(self, name):
        self.name = name
        self.nodes = []                         # Liste mit Anhängseln
        self.left = None                        # linkes Anhängsel des Knotens
        self.right = None                       # rechtes Anhängsel des Knotens

    def getname(self):
        return self.name

class BDDEVENT: 
    def __init__(self,name):                
        self.name = name
        self.left = None                        # linkes Anhängsel des Events
        self.right = None                       # rechtes Anhängsel des Events

    def getname(self):
        return self.name

class FT2BDD:
    def __init__(self):
        self.nroot = None                       # Wurzelknoten
        self.ZERO = "Stub0"                     # linke Null des BDD
        self.ONE = "Stub1"                      # rechte Eins des BDD
        self.new_nodes = []                     # Knoten des BDD
        
    def show(self):
        bdd_graph = gv.Digraph("Graph")                             
        bdd_graph.attr("graph",splines="spline")                           
        for element in self.new_nodes:                                 # läuft über die liste new_nodes de BDD
            if isinstance(element,BDDEVENT):                           # Falls das Element ein BDDEvent ist,
                if isinstance(element.left, BDDEVENT):                 # Falls das linke Element ein BDDEvent ist,
                    bdd_graph.edge(element.name, element.left.name)    # erstelle Kante vom BDDEvent an das linke BDDEvent
                else:                                                  # sonst
                    bdd_graph.edge(element.name, element.left)         # erstelle Kante vom BDDEvent an die linke Null (Stub0)
                if isinstance(element.right, BDDEVENT):                # falls das rechte ELement ein BDDEvent ist, 
                    bdd_graph.edge(element.name, element.right.name)   # erstelle Kante vom BDDEvent an das rechte BDDEvent
                else:                                                  # sonst
                    bdd_graph.edge(element.name, element.right)        # erstelle Kante vom BDDEvent an die rechte Eins (Stub1)    
        bdd_graph.render('result2.gv', view = True)                    # speichert Graph im PDF
                                                        
    def create(self,ntop,ft):                        
        if ntop == None:                        # Falss es den Top-Knoten nicht gibt, 
            ntop = NODE("root")                 # erstelle einen Node mit dem Namen root

        if self.nroot == None:                  # Falls aktueller nroot kein Wert zugewiesen hat,
            self.nroot = ntop                   # setze ihn auf ntop

        if isinstance(ft, ANDNODE):             # Falls ft ein Andnode ist,        
            self.createand(ntop,ft)             # rufe die Funktion createand auf
        elif isinstance(ft, ORNODE):            # Falls ft ein Ornode ist,
            self.createor(ntop,ft)              # rufe die Funktion createor auf
        else:
            print(ft.name)                      # sonst Fehlermeldung         
            assert(False)

    def createand(self,ntop,ft):                  
        print("->createand")
        temp_nodes = []
        
        for element in ft.nodes:                                                                            # For-Schleife über die angeehängten Elemente von ft                     
            if isinstance(element,EVENT) or isinstance(element,ANDNODE) or isinstance(element,ORNODE):      # Falls das Element ein Event, ein Andnode oder ein Ornode ist,
                node = BDDEVENT(element.name) if isinstance(element, EVENT) else NODE(element.name)         # erstelle ein BDDEvent mit dem Namen des Events, des Andnode oder des Ornode und weise es der Var. node zu                 
                temp_nodes.append(node)                                                                     # hänge node an die Liste temp_nodes
                self.new_nodes.append(node)                                                                 # hänge node an die Liste new_nodes
        
        temp_nodes[0].left, temp_nodes[1].left = self.ZERO, self.ZERO                                   # hängt an den ersten und zweiten Listeneintrag (Node oder BDD Event) links die Null an                    
        temp_nodes[0].right, temp_nodes[1].right = temp_nodes[1], self.ONE                              # hängt an den ersten Listeneintrag rechts den zweiten Listeneintrag, an den zweiten rechts die Eins an
        # -> Andnode ist rechtsläufig

        list(map(lambda e: self.create(ntop, e), filter(lambda e: not isinstance(e, EVENT), ft.nodes))) # falls das Element aus ft.nodes kein Event ist, rufe create mit diesem Knoten auf
        
        for element in temp_nodes:                          # laufe über temp_nodes         
            if isinstance(element.right, NODE):             # wenn der rechte Kindknoten eine Knoten ist,                        
                temp_name = ""
                for old_node in ft.nodes:                   # laufe über ft_nodes
                    if old_node.name != element.name:       # falls der Knoten aus dem Fehlerbaum ungleich ist zu dem Knoten aus temp_nodes
                        temp_name = old_node.nodes[0].name  # weise temp_name den Namen des Kindknotens zu
                for new_node in self.new_nodes:             # laufe über self.new_nodes     
                    if new_node.name == temp_name:          # falls der Knoten den gleichen Namen hat wie die Variable temp_name,
                        element.right = new_node            # weise dem rechten Element den neuen Namen zu.
                
        print("<-createand")
        #return ntop

    def createor(self, ntop,ft):                    
        print("->createor")
        temp_nodes = []

        for element in ft.nodes:
            if isinstance(element,EVENT) or isinstance(element,ANDNODE) or isinstance(element,ORNODE): 
                node = BDDEVENT(element.name) if isinstance(element, EVENT) else NODE(element.name)                 
                temp_nodes.append(node)         
                self.new_nodes.append(node)     
                
        temp_nodes[0].left, temp_nodes[1].left = temp_nodes[1], self.ZERO
        temp_nodes[0].right, temp_nodes[1].right = self.ONE, self.ONE
        # -> Ornode ist linksläufig
               
        list(map(lambda e: self.create(ntop, e), filter(lambda e: not isinstance(e, EVENT), ft.nodes)))
         
        for element in temp_nodes:
            if isinstance(element.left, NODE):
                temp_name = ""
                for old_node in ft.nodes:
                    if old_node.name != element.name: 
                        temp_name = old_node.nodes[0].name 
                for new_node in self.new_nodes:
                    if new_node.name == temp_name:
                        element.left = new_node

        print("<-createor")
        #return ntop

# Fehlerbaum aus Aufgabe:
TOP = ANDNODE("TOP (&)")
A = ANDNODE("A")
E1 = EVENT("E1", 1/1000, 1/4)
E2 = EVENT("E2", 1/1000, 1/4)
E3 = EVENT("E3", 1/1000, 1/4)

TOP.add(E1)
TOP.add(A)
A.add(E2)
A.add(E3)

bdd = FT2BDD()
bdd.create(None,TOP)
bdd.show()