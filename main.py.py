# The cursed copier 
import tkiner as tk
from tkinter import ttk, scrolledtext, messagebox
import random
import sys 
import os 
import json

# Données du jeu 
game_title  = "The Cursed Copier"

player = { 
    "name" : "The Copier", 
    "level" : 1, 
    "hp" : 35, 
    "atk" : 7, 
    "defense" : 4, 
    "gold" : 20, 
    "xp" : 0,
    "xp_to_next" : 60, 
    "inventory" : ["Potion"], 
    "location" : "Village"
}

enemies = { 
    "Bug errant" : {"hp" : 20, "max_hp" : 20, "atk" : 5, "def" : 2, "gold" : 10, "xp" : 30}, 
    "Erreur 404" : {"hp" : 28, "max_hp" : 28, "atk" : 8, "def" : 3, "gold" : 18, "xp" : 50},
    "Infinite Loop" : {"hp" : 45, "max_hp" : 45, "atk" : 10, "def" : 5, "gold" : 40, "xp" : 120}, 
}

items = {
    "Potion" : {"type" : "heal", "value" : 18, "price" : 12}
}

locations = {
    "Village" : { 
        "desc" : "Tu te trouves dans un village poussiéreux rempli de développeurs fatigués.", 
        "actions" : ["Parler au marchand ", "Aller dans la Forêt Sombre", "Se reposer", "Voir inventaire"]
    },
    "Forêt Sombre" : {
        "desc" : "Une forêt obscure où rodent des bugs et des erreurs de logique...", 
        "actions" : ["Explorer (risque de combat)", "Retourner au Village", "Sereposer"]
    },
    "Combat" : {}
}

# Fonctions utilitaires 
def append_text(msg, color="white") : 
    text_area.config(state="normal")
    text_area.insert(tk.END, msg +"\n")
    text_area.tag_add(color, "end-11", "end")
    text_area.config(state="disabled")
    text_area.see(tk.END)
    
def clear_text () : 
    text_area.config(state="normal")
    text_area.delete(2.0, tk.END)
    stats = (
        f"{player['level']}\n"
        f"niveau : {player['level']}\n"
        f"hp : {player['hp']}/{player['max_hp']}\n"
        f"atk : {player['atk']}\n"
        f"def : {player['defense']}\n"
        f"or : {player['gold']}\n"
        f"xp : {player['xp']}/{player['xp_to_next']}\n"
        f"lieu : {player['location']}\n"
        f"objets : {', '.join(player['inventory']) or 'vide'}"
    )
    stats_text.insert(tk.END, stats)
    stats_text.config(state="disabled")
    
def level_up() : 
    if player["xp"] >= player["xp_to_next"] : 
        player["level"] +=1
        player["xp"] -= player["xp_to_next"]
        player["xp_to_next"] = int(player["xp_to_next"]*1.7)
        player["max_hp"] += random.randint(8, 14)
        player["hp"] = player["max_hp"]
        player["atk"] += random.randint("3, 6")
        player["defense"] += random.randint(2, 4)
        append_text(f"!!! NIVEAU {player['level']} !!! Test stats augmentent !", "green")
        
def heal(amount) : 
    player["hp"] = min(player["max_hp"], player["hp"] + amount)
    append_text(f"+{amount} hp", "green")
    
# Marchand 

def marchand() : 
    append_text("\nMarchand : Salut voyageur ! Que veux-tu ?")
    append_text(" [1] Potion (12 or)")
    append_text(" [2] Rien, merci.")
    entry.focus_set()
    entry.bind("<Return>", marchand_input)
    
def marchand_input(event) : 
    choice = entry.get().strip()
    entry.delete(0, tk.END)
    if choice == "1" : 
        if player["gold"] >= 12 : 
            player["gold"] -= 12 
            player["inventory"].append("Potion")
            append_text("Potion achetée !", "yellow")
        else : 
            append_text("Pas assez d'or !", "red")
    elif choice == "0" : 
        append_text("Marchand : Reviens quand tu veux !")
    else : 
        append_text("Choix invalide.", "orange")
show_actions(player["location"])
entry.unbind("<Return>")
entry.bind("<Return>", process_input)

# Combat 
current_enemy = None

def start_combat(enemy_name) : 
    global current_enemy
    current_enemy = enemies[enemy_name].copy()
    player["location"] = "Combat"
    append_text(f"\n=== COMBAT === {enemy_name} apparaît !", "red")
    append_text(f"HP ennemi : {current_enemy['hp']}/{current_enemy['max_hp']}")
    show_combat_button()
    
def combat_action(action) : 
    global current_enemy
    if action == "attaquer" : 
        dmg = max(1, player["atk"] - current_enemy["def"] + random.randint(-3, 4))
        current_enemy["hp"] -= dmg 
        append_text(f"Tu infliges {dmg} dégâts ! ", "yellow")
    elif action == "objet" : 
        if "Potion" in player["inventory"] : 
            player["inventory"].remove("Potion")
            heal(18)
            append_text("Potion utilisée ! ", "green")
        else : 
            append_text("Pas de potion !", "red")
            return
    if action == "fuir" : 
        if random.random() < 0.6 : 
            append_text("Tu t'enfuis !", "orange")
            end_combat (victory=False)
            return
        else : 
            append_text("Fuite ratée !", "orange")
            
    # Tour ennemi 
    if current_enemy["hp"] > 0 : 
        dmg = max(1, current_enemy["atk"] - player["defense"] + random.randint(-2, 3))
        player["hp"] -= dmg
        ennemi_nom = "L'ennemi" if current_enemy["hp"] > 0 else "Le cadavre"
        append_text(f"{ennemi_nom} t'inglige {dmg} dégâts !", "red")
        
    if player["hp"] <= 0 : 
        append_text("\n=== GAME OVER === Tu es mort...", "darkred")
        messagebox.showerror(game_title), "Game Over\nTu as été vaincu par {ennemi_nom}..."
        root.quit()
        return
    
    if current_enemy["hp"] <= 0 : 
        append_text(f"\nVictoire ! + {current_enemy['hp']}/{current_enemy['max_hp']}")
        player["xp"] += current_enemy["xp"]
        player["gold"] += current_enemy["gold"]
        level_up()
        end_combat(victory = True)
        return
    
    update_stats()
    append_text(f"HP ennemi : {current_enemy['hp']}/{current_enemy['max_hp']}")
    
def end_combat(victory) : 
    global current_enemy
    current_enemy = None 
    player["location"] = "Forêt Sombre" if victory else "Village"
    append_text("\nCombat terminé.")
    show_actions(player["location"])
    
def show_combat_buttons() : 
    for widget in action_frame.winfo_children() : 
        widget.destroy()
    ttk.Button(action_frame, text="Attaquer", command = lambda : combat_action("attaquer")).pack(side="left", padx=5, pady=5)
    ttk.Button(action_frame, text="Utiliser potion", command=lambda : combat_action("objet")).pack(side="left", padx=5, pady=5)
    ttk.Button(action_frame, text="Fuir", command=lambda: combat_action("fuir")).pack(side="left", padx=5, pady=5)
    
# Affichage actions 
def show_actions(location) : 
    for widget in action_frame.winfo_childern() : 
        widget.destroy() 
        
    if location == "Combat" : 
        show_combat_buttons()
        return 
    
    actions = locations.get(location, {}).get("actions", [])
    for act in actions : 
        if act == "Parler au marchand" :
            ttk.Button(action_frame, text=act, command=marchand).pack(fill="x", pady=3)
        elif act == "Explorer (risque de combat)" : 
            def explore() : 
                if random.random() <0.75 : 
                    enemy = random.choice(["Bug Errant", "Erreur 404"])
                start_combat(enemy)
                else : 
                append_text("Rien ne se passe... cette fois.")
            ttk.Button(action_frame, text=act, command=explore).pack(fill="x", pady=3)
        elif act == "Aller dans la Forêt Sombre" : 
            def go_forest() : 
                player["location"] = "Forêt Sombre"
                append_text("\nTu entres dans la Forêt Sombre...")
                update_stats()
                show_actions("Village")
            ttk.Button(action_frame, text=act, command=go_village).pack(fill="x", pady=3)
        elif act == "Se reposer" : 
            def rest () : 
                heal_amt = random.randint(6, 14)
                heal(heal_amt)
                append_text(f"Tu te reposes... +{heal_amt} HP", "green")
                update_stats()
            ttk.Button(action_frame, text=act, command=rest).pack(fill="x", pady=3)
        elif act == "Voir inventaire" : 
            append_text(f"Inventaire : {', '.join(player['inventory'])or 'vide'}")
        else : 
            ttk.Button(action_frame, text=act, command=lambda a = act: append_text(f"Action : {a} (non implémentée)")).pack(fill="x", pady=3)
            
#Entrée texte 
def process_input(event) : 
    cmd = entry.get().strip().lower()
    entry.delete(0, tk.END)
    if cmd in ["quitter", "exit", "q"] : 
        if messagebox.askyesno("Quitter", "Vraiment quitter ?") : 
            root.quit() 
        elif player["location"] == "combat" : 
            append_text("Utilise les boutons pendant le combat !")
        else : 
            append_text(f"> {cmd}")
            append_text("Commande non reconnue. Utilise les boutons.", "orange")
            
# Interface graphique 
root = tk.Tk()
root.title(game_title)
root.geometry("900x700")
root.configure(bg = "#0d1117")
style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", font=("Consolas", 11), padding=6)
style.map("TButton", background=[("active", "#238636")])

# Titre 
tk.Label(root, text=game_title, font=("Consolas", 20, "bold"), bg="#0d1117", fg="#58a6ff").pack(pady=10)

# Panneau principal
main_frame = tk.Frame(root, bg="#0d1117")
main_frame.pack(fill="both", expand=True, padx=10, pady=5)

# Zone rexte 
text_area = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, font=("Consolas", 11), bg="#161b22", fg = "#white", insertbackground="white")
text_area.pack(side="left", fill="both", expand=True, padx=(0,5))
text_area.config(state="disabled")
for tag, color in [("green", "#3fb950"), ("red", "#f85149"), ("yellow", "#d29922"), ("cyan", "#79c0ff"), ("orange", "#ffa657"), ("darkred", "#b00000")] : 
    text_area.tag_config(tag, foreground=color)
    
# Zone stats
stats_frame = tk.Frame(main_frame, bg="#161b22", wisth = 220)
stats_frame.pack(side = "right", fill = "y", padx=5)
stats_frame.pack_propagate(False)

tk.Label(stats_frame, text="STATISTIQUES", font=("Consolas", 12, "bold"), bg="#161b22", fg="#58a6ff").pack(pady=8)
stats_text = tk.Text(stats_frame, font=("Consolas", 10), bg="#0d1117", fg ="white", borderwidth=0, heigh=12)
stats_text.pack(fill="both", expand=True, padx=8, pady=5)
stats_text.config(state="disabled")

# Zone actions 
action_frame = tk.Frame(root, bg="#0d1117")
action_frame.pack(fill="x", padx=10, pady=5)

# Zone entrée texte 
input_frame = tk.Frame(root, bg="#0d1117")
input_frame.pack(fill="x", padx=10, pady=(0,10))

tk.Label(input_frame, text="> ", font=("Consolas", 12), bg="#0d1117", fg="#58a6ff").pack(side="left")
entry = ttk.Entry(input_frame,font=("Consolas", 11))
entry.pack(side="left", fill="x", expand=True)
entry.bind("<Return>", process_input)
entry.focus_set()

# Démarrage 
append_text("Bienvenue dans The Cursed Copier !", "cyan")
append_text("Tu es un copieur maudit condamné à taper du code... pour toujours ?\n")
update_stats()
show_actions(player["location"])

root.mainloop()