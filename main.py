import json
import os

def initialize_data_file():
    """creation des fichier de donnes s'ils n'existent pas"""
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"creation de {data_dir}")

    """definition de la stricture du fichier"""
    files = {
        'etudiant.json' : [],
        'professeur.json' : [],
        'module.json' : [],
        'présence.json' : []
    }
    
    for filename , initial_data in files.items():
        filepath = os.path.join(data_dir,filename)
        
        if not os.path.exists(filepath):
            with open(filepath,'w') as f :
                json.dump(initial_data,f,indent=4)
            print(f"creation complete de {filepath}")
        else:
            print(f"{filepath} exist")
            
class personne():
    def __init__(self,id,nom,prenom,email,numero_telephone):
        self.id = id
        self.nom = nom
        self.prenom = prenom
        self.email = email
        self.numero_telephone = numero_telephone
    
    def afficher_donne(self):
        """affichage des donnes"""
        return f"Id : {self.id}\n Nom : {self.nom}\n Prenom : {self.prenom}\n Email : {self.email}\n Numero de telephone : {self.numero_telephone}"

    def to_dict(self):
        """convertir les donnes en dictionnaire pour les stocke en json"""
        return {
            "id":self.id,
            "nom":self.nom,
            "prenom":self.prenom,
            "email":self.email,
            "numero_telephone":self.numero_telephone
        }

class etudiant(personne):
    def __init__(self, id, nom, prenom, email, numero_telephone,modules=None,notes=None):
        super().__init__(id, nom, prenom, email, numero_telephone)
        self.modules = modules if modules else []
        self.notes = notes if notes else {}
    def etudie_module(self,module):
        """ajoute un modules a l'etudiant"""
        if module_id not in self.modules :
            self.modules.append(module_id)
            return True
        return False
    def ajout_note(self,note):
        if module_id in self.modules:
            self.notes[module_id] = note
            return True
        return False
    def calcule_moyenne(self):
        if not self.notes:
            return 0.0
        return sum(self.notes.values()/len(self.notes))
    def afficher_donne(self):
        base_info = super().afficher_donne()
        return f"{base_info}\n modules : {len(self.modules)}\n moyenne : {self.calcule_moyenne():.2f}"
    def to_dict(self):
        data = super().to_dict()
        data["modules"] = self.modules
        data["notes"] = self.notes
        return data
    
if __name__ == '__main__':
    pass