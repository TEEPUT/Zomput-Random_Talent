require "OptionScreens/CharacterCreationProfession"
ZomputRandomTalent = ZomputRandomTalent or {}
local ZRT = ZomputRandomTalent
local Screen = CharacterCreationProfession
require "OptionScreens/CoopCharacterCreationProfession"
ZRT.sessions = ZRT.sessions or setmetatable({}, {__mode = "k"})
local internal, restore

local function sessionKey(screen)
    local coop = CoopCharacterCreation and CoopCharacterCreation.instance
    local deaths = ISPostDeathUI and ISPostDeathUI.instance
    -- Cancel destroys the creation panel and descriptor, but the same death UI
    -- survives until a replacement character is accepted. Each later death has
    -- a different UI, and split-screen players have separate entries.
    if coop and coop.charCreationProfession == screen and deaths then
        local death = deaths[coop.playerIndex]
        if death then return death end
    end
    return MainScreen.instance.desc
end

function ZRT.limit()
    local value = SandboxVars and SandboxVars.ZomputRandomTalent and SandboxVars.ZomputRandomTalent.RollLimit
    if type(value) ~= "number" or value ~= value then return 5 end
    return math.max(1, math.min(100, math.floor(value)))
end

function ZRT.session(screen)
    local key = sessionKey(screen)
    local state = ZRT.sessions[key]
    if not state then
        state = {used = 0, limit = ZRT.limit(), ready = false}
        ZRT.sessions[key] = state
    end
    screen.zrtSession = state
    if state.ready and (state.screen ~= screen or state.desc ~= MainScreen.instance.desc) then
        state.ready = false
        local ok = restore(screen, state)
        state.ready, state.failed = ok, not ok
    end
    return state
end

internal = function(screen, fn, ...)
    local previous = screen.zrtInternal
    screen.zrtInternal = true
    local ok, result = pcall(fn, screen, ...)
    screen.zrtInternal = previous
    return ok, result
end

local function synchronizeProfession(screen)
    local desc = MainScreen.instance.desc
    if desc.setProfessionSkills then
        desc:setProfessionSkills(screen.profession)
        desc:setCharacterProfession(screen.profession:getType())
    end
end

restore = function(screen, state)
    return internal(screen, function(self)
        self:resetBuild()
        local index = state.professionIndex
        if state.professionType then
            index = nil
            for i, entry in ipairs(self.listboxProf.items) do
                if entry.item:getType() == state.professionType then index = i; break end
            end
        end
        if not index or not self.listboxProf.items[index] then error("Saved profession unavailable") end
        self.listboxProf.selected = index
        self:onSelectProf(self:getSelectedProf())
        self:removeAllTraits()
        for _, traitType in ipairs(state.traits) do
            local trait = CharacterTraitDefinition.getCharacterTraitDefinition(traitType)
            if not trait then error("Saved trait unavailable") end
            self:addTrait(trait)
        end
        self:checkXPBoost()
        synchronizeProfession(self)
        state.screen, state.desc = self, MainScreen.instance.desc
    end)
end

function ZRT.roll(screen)
    local state = ZRT.session(screen)
    if screen.zrtInternal or state.used >= state.limit then return false end
    -- Consume before execution: a partial failure must never grant a free reroll.
    state.used = state.used + 1
    state.ready = false
    local ok = internal(screen, function(self)
        if #self.listboxProf.items == 0 then error("No professions") end
        self:resetBuild()
        self.listboxProf.selected = ZombRand(#self.listboxProf.items) + 1
        self:onSelectProf(self:getSelectedProf())
        self:removeAllTraits()
        -- Reuse vanilla add/remove validation for profession traits, exclusions,
        -- sandbox-disabled traits, dependencies and derived granted traits.
        for _, entry in ipairs({{self.listboxTrait, self.addGoodTrait},
            {self.listboxBadTrait, self.addBadTrait}}) do
            local attempts = ZombRand(5) + 1
            for i = 1, attempts do
                if #entry[1].items > 0 then
                    entry[1].selected = ZombRand(#entry[1].items) + 1
                    entry[2](self)
                end
            end
        end
        self:checkXPBoost()
        -- The UI may be reused with a replacement descriptor. Vanilla skips
        -- onSelectProf's body when the selected profession has not changed.
        synchronizeProfession(self)
        state.professionIndex = self.listboxProf.selected
        state.professionType = self.profession.getType and self.profession:getType() or nil
        state.traits = {}
        for _, entry in ipairs(self.listboxTraitSelected.items) do
            if not entry.item:isFree() then state.traits[#state.traits + 1] = entry.item:getType() end
        end
        state.screen, state.desc = self, MainScreen.instance.desc
    end)
    state.ready = ok
    state.failed = not ok
    return ok
end

-- Guard the mutation methods themselves: mouse double-clicks, controller
-- shortcuts and presets must follow the same rule as the visible buttons.
for _, name in ipairs({"addGoodTrait", "addBadTrait", "addTrait", "removeTrait",
    "removeAllTraits", "resetTraits", "resetBuild", "loadBuild"}) do
    local original = Screen[name]
    Screen[name] = function(self, ...)
        if self.zrtInternal or not self.zrtSession then return original(self, ...) end
    end
end

-- Split-screen/respawn uses a subclass whose Next handler bypasses the base
-- callback. Guard it separately before it opens the appearance screen.
local coopOption = CoopCharacterCreationProfession.onOptionMouseDown
function CoopCharacterCreationProfession:onOptionMouseDown(button, ...)
    if button and button.internal == "NEXT" and not ZRT.session(self).ready then return end
    return coopOption(self, button, ...)
end
local selectProfession = Screen.onSelectProf
function Screen:onSelectProf(profession)
    if self.zrtInternal or not self.zrtSession then return selectProfession(self, profession) end
end

function Screen:randomizeTraits() return ZRT.roll(self) end
local option = Screen.onOptionMouseDown
function Screen:onOptionMouseDown(button, ...)
    local action = button and button.internal
    if action == "RANDOMIZE" then ZRT.roll(self); return end
    if action == "ADDTRAIT" or action == "ADDBADTRAIT" or action == "REMOVETRAIT"
        or action == "RESETTRAITS" then return end
    if action == "NEXT" and not ZRT.session(self).ready then return end
    return option(self, button, ...)
end

function ZRT.refresh(screen)
    if not screen.randomButton then return end
    local state = ZRT.session(screen)
    for _, name in ipairs({"addTraitBtn", "addBadTraitBtn", "removeTraitBtn", "resetButton"}) do
        if screen[name] then screen[name]:setEnable(false) end
    end
    if screen.presetPanel then screen.presetPanel:setVisible(false) end
    if screen.resetButton then screen.resetButton:setVisible(false) end
    if state.professionIndex then screen.listboxProf.selected = state.professionIndex end
    screen.randomButton:setEnable(state.used < state.limit)
    screen.randomButton:setTooltip(getText(state.failed and "IGUI_ZRT_Failed" or "IGUI_ZRT_Hint"))
    screen.playButton:setEnable(state.ready)
    local nextTooltip
    if not state.ready then nextTooltip = getText("IGUI_ZRT_Required") end
    screen.playButton:setTooltip(nextTooltip)
end

local visible = Screen.setVisible
function Screen:setVisible(value, ...)
    local result = visible(self, value, ...)
    if value then ZRT.refresh(self) end
    return result
end
local prerender = Screen.prerender
function Screen:prerender(...)
    prerender(self, ...)
    ZRT.refresh(self)
end
local render = Screen.render
function Screen:render(...)
    render(self, ...)
    -- Keep real point totals visible, but neutralize vanilla's negative-point
    -- Next-button restriction only after a successful random roll.
    ZRT.refresh(self)
    local state = self.zrtSession
    if state and self.randomButton then
        local text = getText("IGUI_ZRT_Remaining", state.limit - state.used, state.limit)
        self:drawTextRight(text, self.randomButton:getX() - 10,
            self.randomButton:getY() + (self.randomButton:getHeight() - getTextManager():getFontHeight(UIFont.Small)) / 2,
            0.95, 0.85, 0.45, 1, UIFont.Small)
    end
end
