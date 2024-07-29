from mvlocscript.xmltools import xpath

CUSTOM_FONT = {
    'fuel': '{',
    'droneparts': '|',
    'drones': '|',
    'missiles': '}',
    'scrap': '~',
    'repair': '$',
    'elite': '€',
    'fire': '‰',
    'power': '†',
    'cooldown': '‡',
    #'upgraded': '™'
}

class EventBaseClass():
    def __init__(self, element, priority) -> None:
        self._element = element
        self._priority = priority
        self._infoText = None
    
    @property
    def priority(self):
        return self._priority
    
    def setInfo(self):
        raise NotImplementedError
    
    def getInfo(self):
        self.setInfo()
        return self._infoText

def ajustText(text, use_custom_font = True):
    if text is None:
        return None
    
    if use_custom_font:
        text = text.lower()
        for key, custom_font in CUSTOM_FONT.items():
            text = text.replace(key, custom_font)
    return text.replace('_', ' ').title()


#----------------------Evnets----------------------

class NameReturn():
    '''Contain fixed event'''
    def __init__(self, name, priority=1) -> None:
        self._priority = priority
        self._infoText = name
    
    @property
    def priority(self):
        return self._priority
    
    def getInfo(self):
        return self._infoText
    
class TextReturn(EventBaseClass):
    '''A proxy of loadEvent and this deals with <textReturn>.'''
    def __init__(self, element, priority=1) -> None:
        super().__init__(element, priority)
    
    def setInfo(self):
        self._infoText = self._element.text or None

class UnlockCustomShip(EventBaseClass):
    '''Deal with <unlockCustomShip>.'''
    def __init__(self, element, priority=999) -> None:
        super().__init__(element, priority)
    
    def setInfo(self):
        text = ajustText(self._element.text.replace('PLAYER_SHIP_', ''), False)
        self._infoText = f'<#>Unlock Ship({text})'

class RemoveCrew(EventBaseClass):
    '''Deal with <removeCrew>.'''
    def __init__(self, element, priority=1) -> None:
        super().__init__(element, priority)
    
    def setInfo(self):
        clonetags = xpath(self._element, './clone')
        if len(clonetags) != 1:
            print('Warning in RemoveCrew: There are multiple <clone> tags or no such tags.')
            self._infoText = '<!>Lose your crew(?)'
            return
        if clonetags[0].text == 'true':
            self._infoText = '<!>Lose your crew(clonable)'
        elif clonetags[0].text == 'false':
            self._infoText = '<!>Lose your crew(UNCLONABLE)'
        else:
            print('Warning in RemoveCrew: <clone>.text was expected as "true" or "false", but an unknown word came: ', clonetags[0].text) 
            self._infoText = '<!>Lose your crew(?)'

class CrewMember(EventBaseClass):
    '''Deal with <crewMember>. This shows crew gain info if "amount" is plus, otherwise crew loss(unclonable) info if "amount" is minus.'''
    def __init__(self, element, priority=1) -> None:
        super().__init__(element, priority)
    
    def setInfo(self):
        try:
            amount = int(self._element.get('amount'))
        except ValueError as e:
            print(e)
            return
        
        if amount > 0:
            race = ajustText(self._element.get('class', 'Random').replace('LIST_CREW_', ''), False)
            self._infoText = f'Gain a crew({race})'
        elif amount < 0:
            self._infoText = '<!>Lose your crew(UNCLONABLE)'

class CrewMember_CrewLossOnly(EventBaseClass):
    '''Deal with <crewMember> only when "amount" is minus and show crew loss(unclonable) info.'''
    def __init__(self, element, priority=1) -> None:
        super().__init__(element, priority)
    
    def setInfo(self):
        try:
            amount = int(self._element.get('amount'))
        except ValueError as e:
            print(e)
            return
        
        if amount < 0:
            self._infoText = '<!>Lose your crew(UNCLONABLE)'

class RevealMap(EventBaseClass):
    '''Deal with <revealMap>.'''
    def __init__(self, element, priority=1) -> None:
        super().__init__(element, priority)
    
    def setInfo(self):
        self._infoText = 'Map Reveal'

class AutoReward(EventBaseClass):
    '''Deal with <autoReward>.'''
    def __init__(self, element, priority=1) -> None:
        super().__init__(element, priority)
    
    def setInfo(self):
        level = self._element.get('level', '?')[0]
        stuff_type = ajustText(self._element.text)
        self._infoText = f'Reward {stuff_type}({level})'

class ItemModify(EventBaseClass):
    '''Deal with <itemModify>.'''
    def __init__(self, element, priority=1) -> None:
        super().__init__(element, priority)
    
    def setInfo(self):
        itemtags = xpath(self._element, './item')
        if len(itemtags) == 0:
            return
        
        itemlist = []
        for itemtag in itemtags:
            item = ajustText(itemtag.get('type'))
            amount_min = itemtag.get('min')
            amount_max = itemtag.get('max')
            try:
                amount_min = int(amount_min)
                amount_max = int(amount_max)
            except ValueError as e:
                print(e)
                continue
            
            if amount_min == amount_max:
                itemlist.append(f'{item}{amount_min}')
            else:
                itemlist.append(f'{amount_min}≤{item}≤{amount_max}')
        self._infoText = ' '.join(itemlist)

class ModifyPursuit(EventBaseClass):
    '''Deal with <modifyPursuit>.'''
    def __init__(self, element, priority=1) -> None:
        super().__init__(element, priority)
    
    def setInfo(self):
        amount = self._element.get('amount')
        if amount is None:
            return
        try:
            amount = int(amount)
        except ValueError as e:
            print(e)
            return
        
        if amount < 0:
            self._infoText = f'Fleet Delay({str(amount * -1)})'
        elif amount > 0:
            self._infoText = f'<!>Fleet Advance({str(amount)})'

class Reward(EventBaseClass):
    '''Deal with <weapon>, <drone>, and <augment>.'''
    def __init__(self, element, priority=1) -> None:
        super().__init__(element, priority)
    
    def setInfo(self):
        name = ajustText(self._element.get('name', '?'), False)
        if self._element.tag[0] in ('a', 'e', 'i', 'o', 'u'):
            self._infoText = f'Gain an {self._element.tag}({name})'
        else:
            self._infoText = f'Gain a {self._element.tag}({name})'

class Damage(EventBaseClass):
    '''Deal with <damage>.'''
    def __init__(self, element, priority=1) -> None:
        super().__init__(element, priority)
    
    def setInfo(self):
        amount = self._element.get('amount')
        if amount is None:
            return
        try:
            amount = int(amount)
        except ValueError as e:
            print(e)
            return
        
        if amount < 0:
            self._infoText = f'Repair Hull({str(amount * -1)}$)'
        elif amount > 0:
            self._infoText = f'<!>Damage Hull({str(amount)})'

class Upgrade(EventBaseClass):
    '''Deal with <upgrade>.'''
    def __init__(self, element, priority=1) -> None:
        super().__init__(element, priority)
    
    def setInfo(self):
        system = ajustText(self._element.get('system'))
        amount = self._element.get('amount')
        if system is None or amount is None:
            return
        
        self._infoText = f'System Upgrade({system} x{amount})'

class Boarders(EventBaseClass):
    '''Deal with <boarders>.'''
    def __init__(self, element, priority=1) -> None:
        super().__init__(element, priority)
    
    def setInfo(self):
        race = ajustText(self._element.get('class', '?').replace('LIST_CREW_', ''), False)
        amount_min = self._element.get('min')
        amount_max = self._element.get('max')
        try:
            amount_min = int(amount_min)
            amount_max = int(amount_max)
        except ValueError as e:
            print(e)
            self._infoText = f'<!>Enemy Boarding({race})'
            return
        
        if amount_min == amount_max:
            self._infoText = f'<!>Enemy Boarding(x{str(amount_min)} {race})'
        else:
            self._infoText = f'<!>Enemy Boarding(x{str(amount_min)}-x{str(amount_max)} {race})'

class Test(EventBaseClass):
    def __init__(self, element, priority) -> None:
        super().__init__(element, priority)


#not done(or not planned to implement): 'environment', 'recallBoarders', 'achievement', 'choiceRequiresCrew', 'instantEscape', 'win', 'lose'
EVENTCLASSMAPS = {
    "Full": {
        "textReturn": TextReturn,
        "unlockCustomShip": UnlockCustomShip,
        "removeCrew": RemoveCrew,
        "crewMember": CrewMember,
        "reveal_map": RevealMap,
        "autoReward": AutoReward,
        "item_modify": ItemModify,
        "modifyPursuit": ModifyPursuit,
        "weapon": Reward,
        "drone": Reward,
        "augment": Reward,
        "damage": Damage,
        "upgrade": Upgrade,
        "boarders": Boarders
    },
    "ShipUnlock+CrewLoss": {
        "unlockCustomShip": UnlockCustomShip,
        "removeCrew": RemoveCrew,
        "crewMember": CrewMember_CrewLossOnly
    }
}