label encounter_battle:
    play music here.stage.bgm2
    python:
        enemy=[]
        for i in renpy.random.choice(here.stage.encounter):
            enemy.append(copy(i))
        for i in enemy:
            if here.stage.levelize != None and i.level < here.stage.levelize:
                i.level = here.stage.levelize
            if renpy.random.random()<.45-difficulty/10:
                i.level +=1
                if renpy.random.random()<.35-difficulty/10:
                    i.level += 1
                    if renpy.random.random()<.2-difficulty/10:
                        i.level += 1
    call battle
    play music here.stage.bgm1
    $ automouse_move(683, 350, 100)
    return

label battle(escape=.6, talk=None, torn=None, naked=None, gameover="gameover"):
    python:
        torntalked=0
        nakedtalked=0
        for i in party[0:3]+enemy:
            i.agile = int(i.max_agile*renpy.random.random())+10
            if i.agile>i.max_agile:
                i.agile=i.max_agile
        _game_menu_screen = None
        partytarget=enemy[0]
        renpy.layer_at_list(at_list=[pan], layer='back')
        if len(enemy)==1:
            enemy[0].xpos = .4
        elif len(enemy)==2:
            enemy[0].xpos, enemy[1].xpos =.25,.55
        else:
            enemy[0].xpos, enemy[1].xpos, enemy[2].xpos =.18,.4,.62
        renpy.show ("shadow1", at_list=[showin(enemy[0].xpos)])
        renpy.show (enemy[0].image_current, at_list=[showin(enemy[0].xpos)])
        if len(enemy)==3:
            renpy.show ("shadow3", at_list=[showin(enemy[2].xpos)])
            renpy.show(enemy[2].image_current, at_list=[showin(enemy[2].xpos)])
        if len(enemy) > 1:
            renpy.show ("shadow2", at_list=[showin(enemy[1].xpos)])
            renpy.show(enemy[1].image_current, at_list=[showin(enemy[1].xpos)])
        hard(.3)
        partyaction = "manual"
        inbattle=True
    if talk is not None:
        $ config.skipping = None
        $ rollback()
        $ renpy.call(talk)
    show screen battle_ui(enemy_num=len(enemy))
    $ automouse_move(145, 515, 100)
    while True:
        if torn is not None and enemy[0].cos > 1 and torntalked ==0:
            hide screen cancel_screen
            hide screen battle_ui
            $ config.skipping = None
            $ rollback()
            $ renpy.call(torn)
            $ torntalked=1
            show screen battle_ui
        if naked is not None and enemy[0].cos > 1 and nakedtalked ==0:
            hide screen cancel_screen
            hide screen battle_ui
            $ config.skipping = None
            $ rollback()
            $ renpy.call(naked)
            $ nakedtalked=1
            show screen battle_ui
        $ rollback(False)
        window show
        python:
            command=0
            for i,j in enumerate(enemy):
                if partytarget.vital>0:
                    break
                partytarget=enemy[0+i]
            while command<3 and partyaction=="manual":
                if party[command].vital >0:
                    renpy.show(party[command].image_current, layer="screens", zorder=2, at_list=[smooth_side])
                    party[command].skill = globals()[renpy.call_screen("command_screen", who=party[command])]
                    renpy.hide(party[command].image, layer="screens")
                    party[command].target = partytarget
                else:
                    party[command].skill = Recover
                if party[command].skill==Cancel:
                    command -= 1
                    if command >=0 and party[command].vital == 0:
                        command -= 1
                    if command >=0 and party[command].vital == 0:
                        command -= 1
                    if command < 0:
                        partyaction=renpy.call_screen("escape_screen")
                        command = 0
                else:
                    command +=1
        window hide
        python:
            if partyaction == "escape":
                if renpy.random.random() < escape -.1+difficulty*.2:
                    renpy.jump("battle_end")
                else:
                    for i in party[0:3]:
                        i.agile = i.agile/2
                    renpy.music.play("fail", channel="sound2")
                    renpy.show("finish", at_list=[popupfinish(.5)], layer="topscreen",
                                what=Text("Escape Failed", size=140, italic=True, color= "#fdd", font="DaftFont.TTF",
                                    outlines=[(2, "f33"), (4, "#f33c"), (0,"#0006",6,6)]))
                    renpy.pause(1.0*persistent.battlespeed)
                    renpy.hide("finish", layer="topscreen")
                    partyaction = "manual"
                    for i in party[0:3]:
                        i.skill=Recover
            elif partyaction == "auto":
                for i in party[0:3]:
                    i.skill = i.auto()
                    i.target = partytarget
            for i in party[0:3]:
                i.speed = (i.skill.speed+i.dex)*(1+renpy.random.random())+i.level
                i.agile -= i.skill.cost
            for i in enemy:
                if transform_event:
                    transform_event=False
                    i.skill = Transform
                else:
                    i.skill = i.auto()
                i.agile -= i.skill.cost
                i.speed = (i.skill.speed+i.dex)*(1+renpy.random.random())+i.level
                i.target = renpy.random.choice(party[0:3])
            order = party[0:3] + enemy
            order.sort(key=attrgetter('speed'), reverse=True)
        show screen cancel_screen
        python:
            for i in order:
                if i.vital>0:
                    i.offence(i.skill, i.target)
                if party[0].vital==0 and party[1].vital==0 and party[2].vital==0:
                    renpy.jump(gameover)
                if enemy[0].vital==0:
                    if len(enemy)==1: renpy.jump("battle_victory")
                    elif enemy[1].vital==0:
                        if len(enemy)==2: renpy.jump("battle_victory")
                        elif enemy[2].vital==0: renpy.jump("battle_victory")
            for i in party+enemy:
                i.restoration()
        hide screen cancel_screen

label battle_victory:
    python:
        hard(.3)
        config.skipping = None  
        gain=0
        for j in enemy:
            for i in party[0:3]:
                i.getexp(j)
                if i.exp > 99:
                    i.exp=0
                    i.level += 1
                    narrator("[i.name] Leveled Up![nw10]")
            gain += int(j.level*difficulty)
        ether += gain
        narrator("You earned [gain] Ether![nw10]") 
        for j in enemy:
            if j.drop != "" and renpy.random.random()<.01:
                getitem = globals()[j.drop]
                renpy.music.play("heal3", channel="sound2")
                items.append(copy(getitem))
                narrator("You earned [getitem.name!t]![nw10]")
            if renpy.random.random()<.005:
                getitem = renpy.random.choice(item_list0)
                renpy.music.play("heal3", channel="sound2")
                items.append(copy(getitem))
                narrator("You earned [getitem.name!t]![nw10]")
    jump battle_end

label battle_end:
    $ config.skipping = None  
    hide screen cancel_screen
    hide screen battle_ui
    scene
    $ renpy.scene(layer="screens")
    $ renpy.scene(layer="topscreen")
    python:
        renpy.layer_at_list(at_list=[panreset], layer='back')
        inbattle=False
        for i in party[0:3]:
            i.reset()
        hard(.3)
        _game_menu_screen = "party_screen"
    return

label gameover:
    $ config.skipping = None  
    window hide
    hide screen cancel_screen
    hide screen battle_ui
    stop music fadeout 1
    scene black with Dissolve(1.0)  
    play sound "gameover"    
    $ renpy.show("text", at_list=[truecenter],what=Text("game over", size=140, italic=True, color= "#fdd"))
    with Dissolve(1.0)
    pause
    hide text with Dissolve(1.0)
    stop sound
    python:
        if difficulty==.5:
            renpy.full_restart()
        else:
            _game_menu_screen = "party_screen"
            
            ether = int(ether/2)
            inbattle=False
            pop_return=True
    jump inn

init -1 python:


    class Actor(renpy.store.object):
        def __init__(self, who, name="", level=0, vital=0, agile=0, str=0, int=0, dex=0, res=0, 
            skills=[], abilities=[], drop="", ai="normal", ypos=.4, cost=0, j_name=""):
            self.name = name
            self.image = who.lower()
            if boot:
                renpy.image("{} normal".format(self.image), Image("small/{}/1.png".format(self.image.rstrip("1").rstrip("2").rstrip("3"))))
                renpy.image("{} torn".format(self.image), Image("small/{}/2.png".format(self.image.rstrip("1").rstrip("2").rstrip("3"))))
                renpy.image("{} naked".format(self.image), Image("small/{}/3.png".format(self.image.rstrip("1").rstrip("2").rstrip("3"))))
                renpy.image("cutin {} normal".format(self.image), Image("sprites/{}/1.png".format(self.image.rstrip("1").rstrip("2").rstrip("3"))))
                renpy.image("cutin {} torn".format(self.image), Image("sprites/{}/2.png".format(self.image.rstrip("1").rstrip("2").rstrip("3"))))
                renpy.image("cutin {} naked".format(self.image), Image("sprites/{}/3.png".format(self.image.rstrip("1").rstrip("2").rstrip("3"))))
                if ypos < .5:
                    self.who = globals()[who.lower()] = Character(name, image=self.image, show_box_pos="c")
                    globals()["{}_l".format(who.lower())] = Character(name, image=self.image, show_box_pos="l")
                    globals()["{}_r".format(who.lower())] = Character(name, image=self.image, show_box_pos="r")
                else:   
                    self.who = globals()[who.lower()] = Character(name, image=self.image, show_box_pos="a")
                    globals()["{}_l".format(who.lower())] = Character(name, image=self.image, show_box_pos="la")
                    globals()["{}_r".format(who.lower())] = Character(name, image=self.image, show_box_pos="ra")
                globals()["{}_b".format(who.lower())] = Character(name, image=self.image, show_box_pos="b")
                globals()["{}_lb".format(who.lower())] = Character(name, image=self.image, show_box_pos="lb")
                globals()["{}_rb".format(who.lower())] = Character(name, image=self.image, show_box_pos="rb")
                globals()["{}_lt".format(who.lower())] = Character(name, image=self.image, show_box_pos="lt")
                globals()["{}_rt".format(who.lower())] = Character(name, image=self.image, show_box_pos="rt")
            self.image_current = self.image+" normal"            
            self.level=level
            self.exp=0
            self.vital = vital
            self.max_vital=vital
            self.agile=agile
            self.max_agile=agile
            self.str=str
            self.int=int
            self.dex=dex
            self.res=res
            self.skills=skills
            self.max_slot=len(skills)
            self.abilities=abilities 
            self.ai=ai
            self.drop=drop
            self.target=None
            self.skill=None
            self.xpos=.85
            self.ypos =ypos
            self.cost=cost
            self.outfit=None
            self.outfit_reserve = None
            self.cos=1
            self.j_name=j_name
            self.info=""
        
        def change(self):
            if chosen_item:
                chosen_item.use(self)
            else:
                store.chosen_item = None
                if chosen_reserved == None:
                    store.chosen_reserved = chosen_player
                else:
                    for i in range(6):
                        if party[i] == chosen_player:
                            store.party[i] = chosen_reserved
                        elif party[i] == chosen_reserved:
                            store.party[i]= chosen_player
                    for i,j in enumerate(backup):
                        if backup[i] == chosen_player:
                            store.backup[i] = chosen_reserved
                        elif backup[i] == chosen_reserved:
                            store.backup[i]= chosen_player
                    store.chosen_player = None
                    store.chosen_reserved=None
                    store.backup.sort(key=attrgetter('exp'), reverse=True)
                    store.backup.sort(key=attrgetter('level'), reverse=True)
        
        def equip(self):
            store.chosen_item=None
            store.chosen_player=None
            store.chosen_reserved=None
            self.max_vital=copy(self.outfit.max_vital)
            if self.vital>self.max_vital:
                self.vital=self.max_vital
            self.max_agile=copy(self.outfit.max_agile)
            if self.agile>self.max_agile:
                self.agile=self.max_agile
            self.str=copy(self.outfit.str)
            self.int=copy(self.outfit.int)
            self.dex=copy(self.outfit.dex)
            self.res=copy(self.outfit.res)
            self.skills=copy(self.outfit.skills)
            self.max_slot=copy(self.outfit.max_slot)
            self.abilities=copy(self.outfit.abilities)
            self.cos=copy(self.outfit.cos)
            if self.cos==1:
                self.image_current = "{} normal".format(self.outfit.image)
            if self.cos==2:
                self.image_current = "{} torn".format(self.outfit.image)
            if self.cos==3:
                self.image_current = "{} naked".format(self.outfit.image)
            self.image=self.outfit.image
        
        def buy(self):
            renpy.music.play("heal1", channel="sound2")
            store.outfits.append(self)
            
            store.outfits.sort(key=attrgetter('image'))
            store.outfits.sort(key=attrgetter('cost'))
            store.ether -= self.cost
        
        def get(self):
            renpy.music.play("heal1", channel="sound2")
            store.outfits.append(self)
            store.outfits.sort(key=attrgetter('image'))
            store.outfits.sort(key=attrgetter('cost'))
        
        def restoration(self):
            if self.vital>0:
                rest = self.res-int((self.cos-1)*self.res/2)
                if rest > 0:
                    self.vital += rest
                if self.vital > self.max_vital:
                    self.vital = self.max_vital
        
        def reset(self,heal=False, repair=False):
            self.agile = self.max_agile
            if heal==True:
                self.vital=self.max_vital
            elif heal != False and self.vital>1:
                self.vital += heal
                if self.vital<1:  
                    self.vital=1
            if self.vital>self.max_vital:
                self.vital=self.max_vital
            if repair==True:
                self.cos=1
                self.image_current = self.image+" normal"
                if self.outfit != None:
                    self.outfit.image_current = "{} normal".format(self.outfit.image)
            elif repair < 0:
                if self.cos==1 and repair==-1:
                    self.cos =2
                    self.image_current = self.image+" torn"
                    if self.outfit != None:
                        self.outfit.image_current = "{} torn".format(self.outfit.image)
                else:
                    self.cos =3
                    self.image_current = self.image+" naked"
                    if self.outfit != None:
                        self.outfit.image_current = "{} naked".format(self.outfit.image)
            if  self.outfit_reserve != None:
                self.outfit_reserve.cos=self.outfit.cos 
                self.outfit = self.outfit_reserve
                self.equip()
                self.outfit = globals()["Super{}".format(self.image)]
                self.outfit_reserve = None
        
        def getexp(self, target):
            if self.vital >0:
                if self.level +4 < target.level:
                    self.exp +=  int(24*difficulty)
                elif self.level +4 == target.level:
                    self.exp +=  int(20*difficulty)
                elif self.level +3 == target.level:
                    self.exp +=  int(16*difficulty)
                elif self.level +2 == target.level:
                    self.exp +=  int(12*difficulty)
                elif self.level +1 == target.level:
                    self.exp +=  int(10*difficulty)
                elif self.level == target.level:
                    self.exp +=  int(8*difficulty)
                elif self.level-1  == target.level:
                    self.exp +=  int(6*difficulty)
                elif self.level-2 == target.level:
                    self.exp +=  int(4*difficulty)
                elif self.level-3 == target.level:
                    self.exp +=  int(2*difficulty)
                elif self.level-4 == target.level:
                    self.exp += int(1*difficulty)
                elif self.level-5 == target.level:
                    self.exp += int(.5*difficulty)
        
        def auto(self):
            if self.vital == 0:
                return Recover
            if self.agile<10:
                if self.agile>4 and renpy.random.random()<.2:
                    return Guard
                else:
                    return Recover  
            selection_list = copy(self.skills)
            for i in self.skills:
                if self.agile < globals()[i].cost or (self.cos==1 and globals()[i].state == "Torn") or globals()[i].power < 0:
                    selection_list.remove(i) 
            while True:
                if self.ai=="Recover" and self.agile<self.max_agile/2 and renpy.random.random()<.5:
                    return Recover
                elif self.agile<self.max_agile/3 and renpy.random.random()<.5:
                    return Recover
                selected = globals()[renpy.random.choice(selection_list)] 
                if selected.type == self.ai or renpy.random.random()<.4:
                    return selected
                elif renpy.random.random()<.2:
                    return Guard
                elif self.agile != self.max_agile and renpy.random.random()<.3:
                    return Recover
                else:
                    continue
        
        def offence(self,skill,target):
            if self.skill.image != "":
                renpy.predict(self.skill.image)
            if self in party:
                renpy.show(self.image_current, layer="screens", zorder=2, at_list=[smooth_side])
            if self.skill == Recover:
                self.agile += (self.max_agile-self.agile)/2+10
                if self.agile>self.max_agile:
                    self.agile=self.max_agile
                renpy.show("text", at_list=[popupskill(self.xpos)], layer="topscreen",
                                what=Text("%s"%self.skill.name, size=70, italic=True, color= "#dfd", font="battlestar.ttf",
                                    outlines=[(2, "3f3"), (4, "#3f3c"), (0,"#0006",6,6)]))
                renpy.pause(.5*persistent.battlespeed)
                renpy.hide("text", layer="topscreen")
            elif self.skill == Guard:
                renpy.show("text", at_list=[popupskill(self.xpos)], layer="topscreen",
                                what=Text("%s"%self.skill.name, size=70, italic=True, color= "#ffd", font="battlestar.ttf",
                                    outlines=[(2, "ff3"), (4, "#ff3c"), (0,"#0006",6,6)]))
                renpy.pause(.5*persistent.battlespeed)
                renpy.hide("text", layer="topscreen")
            elif self.skill == Transform:
                renpy.show("text", at_list=[popupskill(self.xpos)], layer="topscreen",
                                what=Text("%s"%self.skill.name, size=70, italic=True, color= "#ddf", font="battlestar.ttf",
                                    outlines=[(2, "33f"), (4, "#33fc"), (0,"#0006",6,6)]))
                renpy.pause(.5*persistent.battlespeed)
                renpy.hide("text", layer="topscreen")
                self.outfit_reserve=copy(self)
                if self in party:
                    renpy.hide(self.image, layer="screens")
                else:
                    renpy.hide(self.image)
                self.equip()
                renpy.music.play(Transform.sound, channel="sound")
                if self in party:
                    renpy.show(self.image_current, layer="screens", at_list=[smooth_side])
                else:
                    renpy.show(self.image_current, at_list=[showin(self.xpos)])  
                renpy.with_statement(slowflash)
                renpy.pause(.5*persistent.battlespeed)
            else:
                if self in party:
                    for i,j in enumerate(enemy):
                        if target.vital>0: break
                        target=enemy[0+i]
                if self in enemy:
                    while target.vital==0:
                        target=renpy.random.choice(party[0:3])
                if target in party:
                    if self.skill.type=="Magic":
                        renpy.music.play("chant", channel="sound2")
                        renpy.show("magic", at_list=[circuit(self.xpos)])
                        renpy.show(target.image_current, layer="screens", zorder=2, at_list=[smooth_side])
                    else:
                        renpy.music.play(self.skill.sound, channel="sound")
                        renpy.show(self.image_current, at_list=[centerflashzoom(self.xpos)], layer="screens", zorder=0)
                        renpy.show(target.image_current, layer="screens", zorder=2, at_list=[smooth_side])
                elif target in enemy:
                    if self.skill.type=="Magic":
                        renpy.music.play("chant", channel="sound2")
                        renpy.show("magic", at_list=[sidecircuit], layer="topscreen")
                    else:
                        renpy.music.play(self.skill.sound, channel="sound")
                        renpy.show(self.image_current, at_list=[sideflashzoom], layer="topscreen")
                if self.skill.type == "Magic":                  
                    renpy.show("text", at_list=[popupskill(self.xpos)], layer="topscreen",
                                what=Text("%s"%self.skill.name, size=70, italic=True, color= "#ddf", font="battlestar.ttf",
                                    outlines=[(2, "33f"), (4, "#33fc"), (0,"#0006",6,6)]))
                    renpy.pause(.7*persistent.battlespeed)
                    renpy.hide("text", layer="topscreen")
                    renpy.hide("magic")
                    renpy.hide("magic", layer="topscreen")
                    renpy.music.play(self.skill.sound, channel="sound")
                    if target in enemy:
                        if self.skill.target=="All":
                            renpy.show(self.skill.image,at_list=[effect(.4)])
                        else:                           
                            renpy.show(self.skill.image,at_list=[effect(target.xpos)])
                    else:
                        renpy.show(self.skill.image,at_list=[effect_side], layer="topscreen")
                    renpy.pause(.5)
                else:
                    if target in enemy:
                        if self.skill.target=="All":
                            renpy.show(self.skill.image,at_list=[effect(.4)])
                        else:
                            renpy.show(self.skill.image,at_list=[effect(x=target.xpos)])
                    else:
                        renpy.show(self.skill.image,at_list=[effect_side], layer="topscreen")
                    renpy.show("text", at_list=[popupskill(self.xpos)], layer="topscreen",
                                what=Text("%s"%self.skill.name, size=70, italic=True, color= "#ddf", font="battlestar.ttf",
                                    outlines=[(2, "33f"), (4, "#33fc"), (0,"#0006",6,6)]))
                    renpy.pause(.5*persistent.battlespeed)
                    renpy.hide("text", layer="topscreen")
                if self.skill.target=="All" and target in enemy:
                    for i in enemy:
                        if i.vital >0:
                            i.defence(skill, self)            
                elif self.skill.target=="All" and target in party:
                    target.defence(skill, self) 
                    renpy.hide(target.image, layer="screens") 
                    for i in party[0:3]:
                        if i.vital >0 and i != target:
                            renpy.show(i.image_current, layer="screens", zorder=2, at_list=[smooth_side])
                            i.defence(skill, self) 
                            renpy.hide(i.image, layer="screens") 
                else:
                    target.defence(skill, self)
            if self in party:
                renpy.hide(self.image, layer="topscreen")
                renpy.hide(self.image, layer="screens")
                if self.skill.image != "":
                    renpy.hide(self.skill.image)
            elif target in party:
                renpy.hide(target.image, layer="screens") 
                if self.skill.image != "":
                    renpy.hide(self.skill.image, layer="topscreen")
        
        def defence(self, skill, user):
            hitrate = user.skill.hit + user.dex*5 + user.level*5 - self.level*5 - self.agile
            if self.skill == Guard:
                hitrate -= 25
            elif self.skill ==Recover:
                hitrate += 25
            if "Flying" in self.abilities and user.skill.type == "Grapple":
                hitrate -= self.agile
            elif "Dispel" in self.abilities and user.skill.type == "Magic":
                hitrate -= self.agile
            if user.skill.type == "Magic":
                damagerate = user.skill.power+user.int+user.level-self.level
            elif user.skill.type == "Shot":
                damagerate = user.skill.power+user.str/2+user.dex/2+user.level-self.level
            else:
                damagerate = user.skill.power+user.str+user.level-self.level
            if user.level<self.level:
                damagerate*(10+user.level-self.level)/10
            if "Solidity" in self.abilities and user.skill.attr == "Solid":
                damagerate = damagerate/2
            if "Antishock" in self.abilities and user.skill.attr == "Shock":
                damagerate = damagerate/2
            if "Fireproof" in self.abilities and user.skill.attr == "Fire":
                damagerate = damagerate/2
            if "Thunderproof" in self.abilities and user.skill.attr == "Thunder":
                damagerate = damagerate/2
            if "Astralfield" in self.abilities:
                damagerate = damagerate*3/4
            if damagerate<0: damagerate=0
            if hitrate > renpy.random.randint(0,100):
                if hitrate-75 > renpy.random.randint(0,100):
                    renpy.music.play("critical", channel="sound2")
                    # Edit here
                    if self in party:
                        damage = 0
                        critical=False
                    else:
                        damage = int(damagerate*(2+renpy.random.random()/2))
                        critical=True
                    renpy.show("damage", at_list=[popup(self.xpos)], layer="topscreen",
                    what=Text("%s"%damage, size=100, bold=True, italic=True, color= "#f33",
                        outlines=[(2, "fff"), (4, "#fffc"), (0,"#0006",6,6)]))    
                else:
                    renpy.music.play("hit", channel="sound2")
                    # Edit here
                    if self in party:
                        damage = 0
                    else:
                        damage = int(damagerate*(1+renpy.random.random()/4)) 
                    critical=False
                    renpy.show("damage", at_list=[popup(self.xpos)], layer="topscreen",
                                what=Text("%s"%damage, size=100, bold=True, italic=True, color= "#ff3",
                                    outlines=[(2, "fff"), (4, "#fffc"), (0,"#0006",6,6)]))    
                self.vital -= damage
                self.agile -= damage/2
                if self.agile< 1: self.agile=0
                if self.vital< 1: self.vital=0
                if self in party:
                    renpy.show(self.image, layer="screens", zorder=2, at_list=[shake_side])
                else:
                    renpy.show(self.image, at_list=[shake_center]) 
                hard(.7*persistent.battlespeed)
                renpy.hide("damage", layer="topscreen") 
                if critical==True:
                    if self.vital <= self.max_vital*3/4 and self.cos==1:
                        self.cos=2
                        if self.outfit != None:
                            self.outfit.cos = 2
                            self.outfit.image_current = "{} torn".format(self.outfit.image)
                        if persistent.tornskip == False and persistent.cutin:
                            config.skipping = None  
                        if persistent.cutin and config.skipping == None:
                            load(["{} torn".format(self.image),"cutin {} torn".format(self.image)])
                            renpy.show("semiblack", layer="topscreen")
                            renpy.with_statement(Dissolve(.2))
                            self.image_current = "{} torn".format(self.image)
                            if self in party:
                                renpy.show(self.image_current, layer="screens", zorder=2)
                            else:
                                renpy.show(self.image_current)
                            renpy.music.play("crash", channel="sound")
                            if persistent.battlespeed==1:
                                renpy.show("cutin {} torn".format(self.image), layer="topscreen", at_list=[cutin_slow(self.ypos)])
                                renpy.pause(1.5)
                            else:
                                renpy.show("cutin {} torn".format(self.image), layer="topscreen", at_list=[cutin_fast(self.ypos)])
                                renpy.pause(.8)
                            renpy.scene(layer="topscreen")
                        else:
                            self.image_current = "{} torn".format(self.image)
                            if self in party:
                                renpy.show(self.image_current, layer="screens", zorder=2)
                            else:
                                renpy.show(self.image_current)
                    elif self.vital <= self.max_vital/2 and self.cos==2:
                        self.cos=3
                        if self.outfit != None:
                            self.outfit.cos = 3
                            self.outfit.image_current = "{} naked".format(self.outfit.image)
                        if persistent.tornskip == False and persistent.cutin:
                            config.skipping = None  
                        if persistent.cutin and config.skipping == None:
                            load(["{} naked".format(self.image),"cutin {} naked".format(self.image)])
                            renpy.show("semiblack", layer="topscreen")
                            renpy.with_statement(Dissolve(.2))
                            self.image_current = "{} naked".format(self.image)
                            if self in party:
                                renpy.show(self.image_current, layer="screens", zorder=2)
                            else:
                                renpy.show(self.image_current)               
                            renpy.music.play("crash", channel="sound")
                            if persistent.battlespeed==1:
                                renpy.show("cutin {} naked".format(self.image), layer="topscreen", at_list=[cutin_slow(self.ypos)])                        
                                renpy.pause(1.2)        
                            else:
                                renpy.show("cutin {} naked".format(self.image), layer="topscreen", at_list=[cutin_fast(self.ypos)])                        
                                renpy.pause(.7)
                            renpy.scene(layer="topscreen")
                        else:
                            self.image_current = "{} naked".format(self.image)
                            if self in party:
                                renpy.show(self.image_current, layer="screens", zorder=2)
                            else:
                                renpy.show(self.image_current)
                if self.cos==3 and user.skill == Capture and self.vital > 0:
                    if self.level > user.level or capturing==False:
                        pass
                    else:
                        if not globals()[self.name.rstrip("1").rstrip("2").rstrip("3")] in party+backup:
                            renpy.music.play("heal3", channel="sound2")
                            renpy.show(self.image, at_list=[vanish])
                            renpy.hide(self.image) 
                            if self==enemy[0]:
                                renpy.hide("shadow1")
                            elif self==enemy[1]:
                                renpy.hide("shadow2")
                            elif self==enemy[2]:
                                renpy.hide("shadow3")
                            renpy.show("finish", at_list=[popupfinish(self.xpos)], layer="topscreen",
                                        what=Text("Captured", size=140, italic=True, color= "#dfd", font="DaftFont.TTF",
                                            outlines=[(2, "3f3"), (4, "#3f3c"), (0,"#0006",6,6)]))
                            renpy.pause(1.0*persistent.battlespeed)
                            renpy.hide("finish", layer="topscreen")
                            renpy.pause(.5*persistent.battlespeed)
                            store.backup.append(globals()[self.name.rstrip("1").rstrip("2").rstrip("3")])
                            globals()[self.name.rstrip("1").rstrip("2").rstrip("3")].level=self.level
                            self.vital = 0
                            return
                if self.vital==0:
                    renpy.music.play("vanish", channel="sound2")
                    if self in party:
                        renpy.show(self.image, at_list=[vanish], layer="screens")
                        renpy.hide(self.image, layer="screens")
                    else:
                        renpy.show(self.image, at_list=[vanish])
                        renpy.hide(self.image)
                        if self==enemy[0]:
                            renpy.hide("shadow1")
                        elif self==enemy[1]:
                            renpy.hide("shadow2")
                        elif self==enemy[2]:
                            renpy.hide("shadow3")
                    renpy.show("finish", at_list=[popupfinish(self.xpos)], layer="topscreen",
                                what=Text("Defeated", size=140, italic=True, color= "#fdd", font="DaftFont.TTF",
                                    outlines=[(2, "f33"), (4, "#f33c"), (0,"#0006",6,6)]))
                    renpy.pause(1.0*persistent.battlespeed)
                    renpy.hide("finish", layer="topscreen")
                    renpy.pause(.5*persistent.battlespeed)
            else:
                renpy.music.play("sway", channel="sound2")
                if self in party:
                    renpy.show(self.image, layer="screens", zorder=2, at_list=[sway_r_side])
                else:
                    renpy.show(self.image, at_list=[sway_l_center])
                renpy.pause(.5*persistent.battlespeed)



    def init_actor(boot=0):
        store.actor_list = []
        store.selling_outfits = []
        if boot==1:
            store.boot=1
        else:
            store.boot=0
        for l in renpy.file("actor.tsv"):
            l = l.decode("utf-8")
            a = l.rstrip().split("\t")
            if not a[0] == "":
                globals()[a[0]] = Actor(a[0], a[1], int(a[2]), int(a[3]), int(a[4]), int(a[5]), int(a[6]), int(a[7]), int(a[8]),
                    a[9].split(","), a[10].split(","), a[11], a[12], float(a[13]), int(a[14]), a[15])
                globals()[a[0]+"1"] = Actor(a[0]+"1", a[1]+"1", int(a[2]), int(a[3]), int(a[4]), int(a[5]), int(a[6]), int(a[7]), int(a[8]),
                    a[9].split(","), a[10].split(","), a[11], a[12], float(a[13]), int(a[14]), a[15]+"１")
                globals()[a[0]+"2"] = Actor(a[0]+"2", a[1]+"2", int(a[2]), int(a[3]), int(a[4]), int(a[5]), int(a[6]), int(a[7]), int(a[8]),
                    a[9].split(","), a[10].split(","), a[11], a[12], float(a[13]), int(a[14]), a[15]+"２")
                globals()[a[0]+"3"] = Actor(a[0]+"3", a[1]+"3", int(a[2]), int(a[3]), int(a[4]), int(a[5]), int(a[6]), int(a[7]), int(a[8]),
                    a[9].split(","), a[10].split(","), a[11], a[12], float(a[13]), int(a[14]), a[15]+"３")
                actor_list.append(a[0])
                if not a[14] == "0":
                    selling_outfits.append(globals()[a[0]])
        renpy.file("actor.tsv").close()
        
        for i in actor_list:
            if "Transform" in globals()[i].skills:
                globals()[i].outfit=globals()["Super{}".format(i.lower())]
                globals()[i+"1"].outfit=globals()["Super{}".format(i.lower())]
                globals()[i+"2"].outfit=globals()["Super{}".format(i.lower())]
                globals()[i+"3"].outfit=globals()["Super{}".format(i.lower())]

    init_actor(1)


    class Skill(renpy.store.object):
        def __init__(self, name="", type="", attr = "", target="", state="", cost=15, hit=0, power=0, speed=0,
            sound="", image="", grid=1, j_name="", info=""):
            self.name=name
            self.type=type
            self.attr=attr
            self.target=target
            self.state=state
            self.cost=cost
            self.hit=hit
            self.power=power
            self.speed=speed
            self.sound=sound
            self.image=image
            if self.image != "":
                renpy.image("{}".format(image), anim.Filmstrip("ef/{}.png".format(image), (512,384), (1,grid), .05, loop=False))
            self.j_name=j_name
            if type=="Grapple":
                j_type="格闘"
            elif type=="Shot":
                j_type="射撃"
            elif type=="Magic":
                j_type="魔法"
            if attr=="Solid":
                j_attr="ソリッド"
            elif attr=="Shock":
                j_attr="ショック"
            elif attr=="Fire":
                j_attr="ファイア"
            elif attr=="Thunder":
                j_attr="サンダー"
            elif attr=="Astral":
                j_attr="アストラル"
            if target=="Single":
                j_target="単体"
            elif target=="Self":
                j_target="自身"
            elif target=="All":
                j_target="全体"
            self.info="{}\n Type:{} Attr:{} Target: {} \n Ap: {} Hit: {} Power: {} Speed: {}".format(name,type,attr,target,cost,hit,power,speed)



    for l in renpy.file("skill.tsv"):
        l = l.decode("utf-8")
        a = l.rstrip().split("\t")
        if not a[0] == "":
            if a[4]=="":
                a[4]="Single"         
            if a[5]=="":
                a[5]="Normal"
            globals()[a[0]] = Skill(a[1], a[2], a[3], a[4], a[5], int(a[6]), int(a[7]), int(a[8]), int(a[9]), a[10], a[11], int(a[12]), a[13])
    renpy.file("skill.tsv").close()




screen command_screen:
    zorder 2
    default tt = Tooltip('')
    vbox pos (0.03, 0.635):
        at smoothinout(0.3, -16, 0)
        for i in who.skills:
            if globals()[i].cost <= who.agile and not (globals()[i].state == 'Torn' and who.cos == 1):
                if i == 'Attack':
                    textbutton globals()[i].name:
                        action Return(value=i) xminimum 220 hovered tt.Action(globals()[i].info) default True focus 1
                else:
                    textbutton globals()[i].name:
                        action Return(value=i) xminimum 220 hovered tt.Action(globals()[i].info)
            else:
                if i == 'Attack':
                    textbutton globals()[i].name xminimum 220:
                        action [Play('sound', 'error'), SelectedIf(True)] hovered tt.Action(globals()[i].info) default True
                else:
                    textbutton globals()[i].name xminimum 220:
                        action [Play('sound', 'error'), SelectedIf(True)] hovered tt.Action(globals()[i].info)
        for i in range(4 - len(who.skills)):
            textbutton '' xminimum 220
        if Guard.cost <= who.agile:
            textbutton _('Guard') action Return(value='Guard') xminimum 220 hovered tt.Action(Guard.info)
        else:
            textbutton _('Guard') xminimum 220 action [Play('sound', 'error'), SelectedIf(True)] hovered tt.Action(Guard.info)
        textbutton _('Recover') action Return(value='Recover') xminimum 220 hovered tt.Action(Recover.info)
    if enemy[0].vital > 0:
        button background None area (0, 0, 256, 480) anchor (0.5, 0.0) pos (enemy[0].xpos, 1):
            action [SetVariable('partytarget', enemy[0])] hovered tt.Action(_('Change your target'))
    if len(enemy) > 1:
        if enemy[1].vital > 0:
            button background None area (0, 0, 256, 512) anchor (0.5, 0.0) pos (enemy[1].xpos, 1):
                action [SetVariable('partytarget', enemy[1])] hovered tt.Action(_('Change your target'))
    if len(enemy) > 2:
        if enemy[2].vital > 0:
            button background None area (0, 0, 256, 512) anchor (0.5, 0.0) pos (enemy[2].xpos, 1):
                action [SetVariable('partytarget', enemy[2])] hovered tt.Action(_('Change your target'))
    add flipturn('layout/pointer.png') anchor (0.5, 0.0) pos (partytarget.xpos, 0.14)

    text tt.value pos (0.23, 0.71)

    key 'mouseup_3' action [Play('sound', 'cancel'), Return(value='Cancel')]
    key 'K_BACKSPACE' action [Play('sound', 'cancel'), Return(value='Cancel')]
    key 'K_ESCAPE' action [Play('sound', 'cancel'), Return(value='Cancel')]
    key 'x' action [Play('sound', 'cancel'), Return(value='Cancel')]
    key 'joy_menu' action [Play('sound', 'cancel'), Return(value='Cancel')]

screen image_screen(im, hit=False, dodge=False):
    zorder 2    
    if hit:
        add im xcenter 0.85 yanchor 0.5 ypos 0.75 zoom 0.65 at shake_side
    elif dodge:
        add im xcenter 0.85 yanchor 0.5 ypos 0.75 zoom 0.65 at sway_r_side
    else:
        add im xcenter 0.85 yanchor 0.5 ypos 0.75 zoom 0.65 at smoothinout(0.3, 32, 0)

screen escape_screen:
    zorder 2
    default tt = Tooltip('')
    on 'show' action MouseMove(145, 690, 100)
    fixed:
        at smoothinout(0.3, -16, 0)
        textbutton _('Escape') action Return(value='escape') hovered tt.Action(_('Escape Battle')) xminimum 220 xpos 0.03 ypos 0.8
        if persistent.skipauto:
            textbutton _('Auto Battle') default True action [Skip(), Return(value='auto')] xminimum 220 xpos 0.03 ypos 0.87:
                hovered tt.Action(_('Begin Auto-Battle'))
        else:
            textbutton _('Auto Battle') default True action Return(value='auto') xminimum 220 xpos 0.03 ypos 0.87:
                hovered tt.Action(_('Begin Auto-Battle'))
    key 'mouseup_3' action [Play('sound', 'cancel'), Return(value='manual')]
    key 'K_BACKSPACE' action [Play('sound', 'cancel'), Return(value='manual')]
    key 'K_ESCAPE' action [Play('sound', 'cancel'), Return(value='manual')]
    key 'x' action [Play('sound', 'cancel'), Return(value='manual')]
    key 'joy_menu' action [Play('sound', 'cancel'), Return(value='manual')]

    text tt.value pos (0.23, 0.71)

screen cancel_screen:
    zorder 3
    if partyaction == 'auto':
        textbutton _('Auto Battle') xminimum 220 xpos 0.03 ypos 0.87:
            action [SelectedIf(True), Play('sound', 'cancel'), SetVariable('partyaction', 'manual')]
    key 'mouseup_3' action [Play('sound', 'cancel'), SetVariable('partyaction', 'manual')]
    key 'K_BACKSPACE' action [Play('sound', 'cancel'), SetVariable('partyaction', 'manual')]
    key 'K_ESCAPE' action [Play('sound', 'cancel'), SetVariable('partyaction', 'manual')]
    key 'x' action [Play('sound', 'cancel'), SetVariable('partyaction', 'manual')]
    key 'joy_menu' action [Play('sound', 'cancel'), SetVariable('partyaction', 'manual')]
    use quick_menu

screen battle_ui:
    zorder 3
    fixed:
        at smoothinout(0.3, 0, 16)
        use battle_ui_frame(position=(0.31, 0.93), who=party[0], lv=1)
        use battle_ui_frame(position=(0.5, 0.93), who=party[1], lv=1)
        use battle_ui_frame(position=(0.69, 0.93), who=party[2], lv=1)
    fixed:
        at smoothinout(0.3, 0, -16)
        if enemy[0].vital > 0:
            use battle_ui_frame(position=(enemy[0].xpos, 0.07), who=enemy[0], lv=0)
        if len(enemy) > 1:
            if enemy[1].vital > 0:
                use battle_ui_frame(position=(enemy[1].xpos, 0.07), who=enemy[1], lv=0)
        if len(enemy) > 2:
            if enemy[2].vital > 0:
                use battle_ui_frame(position=(enemy[2].xpos, 0.07), who=enemy[2], lv=0)

screen battle_ui_frame:
    frame area (0, 0, 256, 90) anchor (0.5, 0.5) pos position:
        if who.max_vital > 0:
            vbox yfill True:
                hbox xfill True:
                    if _preferences.language == 'japanese':
                        text '[who.j_name]' size 22 bold True
                    else:
                        text '[who.name]' size 22 bold True

                    text '[who.level:>2]' xalign 1.0 size 22
                hbox xfill True:
                    text 'VP' size 20
                    bar value AnimatedValue(who.vital, who.max_vital, 0.3) yalign 0.6 ymaximum 15 xmaximum 128
                    text '[who.vital:>02]/[who.max_vital:>02]' xalign 1.0 size 20
                hbox xfill True:
                    text 'AP' size 20
                    bar value AnimatedValue(who.agile, who.max_agile, 0.3) yalign 0.6 ymaximum 15 xmaximum 128:
                        left_bar Frame('layout/action.png', 12, 6)
                    text '[who.agile:>02]/[who.max_agile:>02]' xalign 1.0 size 20
# Decompiled by unrpyc: https://github.com/CensoredUsername/unrpyc
