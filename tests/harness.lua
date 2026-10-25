function require() end
UIFont = {Small = 1}
MainScreen = {instance = {desc = {}}}
SandboxVars = {ZomputRandomTalent = {RollLimit = 5}}
function getText(key, a, b) return key .. (a and ':' .. a .. '/' .. b or '') end
function getTextManager() return {getFontHeight = function() return 14 end} end
local seed = 17
function ZombRand(n)
    assert(n > 0, 'empty random range')
    seed = (seed * 37 + 11) % 65521
    return seed % n
end
local function button()
    return {setEnable = function(self, value) self.enabled = value end,
        setTooltip = function(self, value) self.tooltip = value end,
        setVisible = function(self, value) self.visible = value end,
        getX = function() return 200 end, getHeight = function() return 28 end,
        getRight = function() return 250 end, getY = function() return 200 end}
end
CharacterCreationProfession = {}
local S = CharacterCreationProfession
function S:resetBuild() self:removeAllTraits(); self.listboxProf.selected = 1 end
function S:removeAllTraits() self.chosen = {}; self.listboxTraitSelected.items = {}; self.points = 0 end
function S:onSelectProf(value) self.profession = value end
function S:getSelectedProf()
    local entry=self.listboxProf.items[self.listboxProf.selected]
    return entry.item or entry
end
function S:addTrait(value)
    self.chosen[#self.chosen + 1] = value; self.points = self.points - value.cost
    self.listboxTraitSelected.items[#self.listboxTraitSelected.items+1] = {item=value}
end
function S:addGoodTrait() self:addTrait(self.listboxTrait.items[self.listboxTrait.selected]) end
function S:addBadTrait() self:addTrait(self.listboxBadTrait.items[self.listboxBadTrait.selected]) end
function S:removeTrait() self.removed = true end
function S:resetTraits() self.reset = true end
function S:loadBuild() self.loaded = true end
function S:checkXPBoost() self.checked = true end
function S:onOptionMouseDown(button) self.lastAction = button.internal end
function S:setVisible(value) self.visible = value end
function S:prerender() end
function S:render() self.playButton:setEnable(self.points >= 0) end
CoopCharacterCreationProfession = setmetatable({}, {__index = S})
function CoopCharacterCreationProfession:onOptionMouseDown(button)
    if button.internal == 'NEXT' then self.coopNext = true
    else S.onOptionMouseDown(self, button) end
end
local traits = {}
CharacterTraitDefinition = {getCharacterTraitDefinition=function(id) return traits[id] end}
local function trait(id, cost)
    local t={cost=cost,getType=function() return id end,isFree=function() return false end}
    traits[id]=t; return t
end
function makeScreen(class)
    return setmetatable({randomButton = button(), playButton = button(), resetButton = button(),
        addTraitBtn = button(), addBadTraitBtn = button(), removeTraitBtn = button(),
        presetPanel = {setVisible = function(self, value) self.visible = value end},
        listboxProf = {items = {'A', 'B', 'C'}, selected = 1},
        listboxTrait = {items = {trait('good1',8), trait('good2',4)}},
        listboxBadTrait = {items = {trait('bad1',-2)}}, listboxTraitSelected={items={}}, chosen = {}, points = 0,
        drawTextRight = function(self, text) self.counter = text end}, {__index = class or S})
end
