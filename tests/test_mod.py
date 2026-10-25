from pathlib import Path
import json
import re
import unittest
from lupa.lua51 import LuaRuntime

ROOT = Path(__file__).resolve().parents[1]
LUA = ROOT / 'Contents/mods/ZomputRandomTalent/42/media/lua'


class RandomTalentTests(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime()
        self.lua.execute((ROOT / 'tests/harness.lua').read_text(encoding='utf-8'))
        self.lua.execute((LUA / 'client/ZRT/Creation.lua').read_text(encoding='utf-8'))
        self.lua.execute('Z = ZomputRandomTalent; S = makeScreen(); S:setVisible(true)')

    def check(self, code):
        self.lua.execute(code)

    def test_roll_limit_and_exhaustion(self):
        self.check('''
            for i=1,5 do assert(Z.roll(S)); assert(Z.session(S).used == i) end
            local chosen = S.chosen; assert(not Z.roll(S)); assert(S.chosen == chosen)
            S:render(); assert(not S.randomButton.enabled and S.playButton.enabled)
            assert(S.counter == 'IGUI_ZRT_Remaining:0/5')
        ''')

    def test_at_least_one_roll_required_even_for_next_callback(self):
        self.check('''
            S:render(); assert(not S.playButton.enabled)
            S:onOptionMouseDown({internal='NEXT'}); assert(not S.lastAction)
            Z.roll(S); S:onOptionMouseDown({internal='NEXT'}); assert(S.lastAction == 'NEXT')
        ''')

    def test_negative_and_surplus_points_allow_next(self):
        self.check('''
            Z.roll(S)
            for _, points in ipairs({-100, 0, 100}) do
                S.points = points; S:render(); assert(S.playButton.enabled and S.points == points)
            end
        ''')

    def test_manual_mutations_presets_and_profession_are_blocked(self):
        self.check('''
            Z.roll(S); local chosen, profession = S.chosen, S.profession
            S:addGoodTrait(); S:addBadTrait(); S:addTrait({cost=999}); S:removeTrait()
            S:resetTraits(); S:resetBuild(); S:removeAllTraits(); S:loadBuild()
            S:onSelectProf('Manual')
            assert(S.chosen == chosen and S.profession == profession)
            assert(not S.loaded and not S.reset and not S.removed)
            for _, action in ipairs({'ADDTRAIT','ADDBADTRAIT','REMOVETRAIT','RESETTRAITS'}) do
                S:onOptionMouseDown({internal=action}); assert(not S.lastAction)
            end
            S:prerender(); assert(not S.addTraitBtn.enabled and not S.removeTraitBtn.enabled)
            assert(not S.presetPanel.visible)
        ''')

    def test_back_appearance_roundtrip_preserves_budget(self):
        self.check('''
            Z.roll(S); S:setVisible(false); S:setVisible(true)
            assert(Z.session(S).used == 1)
            SandboxVars.ZomputRandomTalent.RollLimit = 99
            assert(Z.session(S).limit == 5)
        ''')

    def test_new_character_gets_new_budget(self):
        self.check('''
            Z.roll(S); MainScreen.instance.desc = {}
            S:setVisible(true); assert(Z.session(S).used == 0 and not Z.session(S).ready)
        ''')

    def test_cancel_respawn_and_reenter_preserves_exhaustion_and_last_build(self):
        self.check('''
            ISPostDeathUI = {instance={[0]={}}}
            CoopCharacterCreation = {instance={playerIndex=0,charCreationProfession=S}}
            for i=1,5 do assert(Z.roll(S)) end
            local state = Z.session(S)
            local types = {}; for i,t in ipairs(S.chosen) do types[i]=t:getType() end
            local profession = S.profession
            -- Vanilla cancel/reopen creates BOTH a new panel and a descriptor.
            local reopened = makeScreen(CoopCharacterCreationProfession)
            MainScreen.instance.desc = {}
            CoopCharacterCreation.instance = {playerIndex=0,charCreationProfession=reopened}
            reopened:setVisible(true)
            assert(Z.session(reopened)==state and state.used==5 and state.ready)
            assert(not Z.roll(reopened) and reopened.profession==profession)
            assert(#reopened.chosen==#types)
            for i,t in ipairs(reopened.chosen) do assert(t:getType()==types[i]) end
            reopened:render(); assert(not reopened.randomButton.enabled and reopened.playButton.enabled)
            reopened:onOptionMouseDown({internal='NEXT'}); assert(reopened.coopNext)
        ''')

    def test_repeated_cancel_does_not_replenish_partial_budget(self):
        self.check('''
            ISPostDeathUI = {instance={[0]={}}}
            CoopCharacterCreation = {instance={playerIndex=0,charCreationProfession=S}}
            assert(Z.roll(S)); assert(Z.roll(S))
            local state=Z.session(S)
            for i=1,8 do
                local reopened=makeScreen(CoopCharacterCreationProfession)
                MainScreen.instance.desc={}
                CoopCharacterCreation.instance={playerIndex=0,charCreationProfession=reopened}
                reopened:setVisible(true)
                assert(Z.session(reopened)==state and state.used==2 and state.limit==5)
                S=reopened
            end
            for i=1,3 do assert(Z.roll(S)) end
            assert(not Z.roll(S))
        ''')

    def test_next_death_and_other_split_screen_player_get_separate_budgets(self):
        self.check('''
            ISPostDeathUI = {instance={[0]={},[1]={}}}
            CoopCharacterCreation = {instance={playerIndex=0,charCreationProfession=S}}
            assert(Z.roll(S)); local first=Z.session(S)
            local other=makeScreen(CoopCharacterCreationProfession)
            MainScreen.instance.desc={}
            CoopCharacterCreation.instance={playerIndex=1,charCreationProfession=other}
            other:setVisible(true); assert(Z.session(other).used==0)
            ISPostDeathUI.instance[0]={} -- a new death, after accepting and playing
            local nextLife=makeScreen(CoopCharacterCreationProfession)
            MainScreen.instance.desc={}
            CoopCharacterCreation.instance={playerIndex=0,charCreationProfession=nextLife}
            nextLife:setVisible(true)
            assert(Z.session(nextLife)~=first and Z.session(nextLife).used==0)
        ''')

    def test_failed_restore_does_not_grant_rolls_or_allow_next(self):
        self.check('''
            ISPostDeathUI = {instance={[0]={}}}
            CoopCharacterCreation = {instance={playerIndex=0,charCreationProfession=S}}
            for i=1,5 do assert(Z.roll(S)) end
            local reopened=makeScreen(CoopCharacterCreationProfession)
            CharacterTraitDefinition.getCharacterTraitDefinition=function() return nil end
            MainScreen.instance.desc={}
            CoopCharacterCreation.instance={playerIndex=0,charCreationProfession=reopened}
            reopened:setVisible(true)
            local state=Z.session(reopened)
            assert(state.used==5 and state.failed and not state.ready)
            assert(not Z.roll(reopened))
            reopened:onOptionMouseDown({internal='NEXT'}); assert(not reopened.coopNext)
        ''')

    def test_restore_matches_profession_type_when_new_screen_order_changes(self):
        self.check('''
            ISPostDeathUI={instance={[0]={}}}
            CoopCharacterCreation={instance={playerIndex=0,charCreationProfession=S}}
            local a={getType=function() return 'A' end}
            local b={getType=function() return 'B' end}
            S.listboxProf.items={{item=a},{item=b}}
            assert(Z.roll(S)); local expected=S.profession:getType()
            local reopened=makeScreen(CoopCharacterCreationProfession)
            reopened.listboxProf.items={{item=b},{item=a}}
            MainScreen.instance.desc={}
            CoopCharacterCreation.instance={playerIndex=0,charCreationProfession=reopened}
            reopened:setVisible(true)
            assert(reopened.profession:getType()==expected)
            assert(Z.session(reopened).used==1 and Z.session(reopened).ready)
        ''')

    def test_reused_screen_synchronizes_new_descriptor_profession(self):
        self.check('''
            local profession = {getType=function() return 'ProfessionType' end}
            S.listboxProf.items = {profession}
            MainScreen.instance.desc.setProfessionSkills = function(self, value) self.skills=value end
            MainScreen.instance.desc.setCharacterProfession = function(self, value) self.profession=value end
            assert(Z.roll(S))
            assert(MainScreen.instance.desc.skills == profession)
            assert(MainScreen.instance.desc.profession == 'ProfessionType')
        ''')

    def test_split_screen_next_is_guarded(self):
        self.check('''
            local coop = makeScreen(CoopCharacterCreationProfession); coop:setVisible(true)
            coop:onOptionMouseDown({internal='NEXT'}); assert(not coop.coopNext)
            coop:onOptionMouseDown({internal='RANDOMIZE'}); assert(Z.session(coop).used == 1)
            coop:onOptionMouseDown({internal='NEXT'}); assert(coop.coopNext)
        ''')

    def test_empty_trait_pools_and_empty_profession_pool(self):
        self.check('''
            S.listboxTrait.items = {}; S.listboxBadTrait.items = {}
            assert(Z.roll(S) and #S.chosen == 0)
            S.listboxProf.items = {}; assert(not Z.roll(S))
            assert(not S.zrtInternal and Z.session(S).used == 2 and not Z.session(S).ready)
        ''')

    def test_errors_are_bounded_and_do_not_unlock_manual_editing(self):
        self.check('''
            S.checkXPBoost = function() error('conflict') end
            assert(not Z.roll(S)); assert(not S.zrtInternal)
            S:addTrait({cost=1}); assert(#S.chosen < 11)
            S:render(); assert(not S.playButton.enabled and Z.session(S).failed)
        ''')

    def test_corrupt_limits_clamp_safely(self):
        self.check('''
            for _, value in ipairs({-1, 0, 1.9, 999}) do
                SandboxVars.ZomputRandomTalent.RollLimit = value
                assert(Z.limit() >= 1 and Z.limit() <= 100 and Z.limit() == math.floor(Z.limit()))
            end
            SandboxVars.ZomputRandomTalent.RollLimit = 0/0; assert(Z.limit() == 5)
            SandboxVars = nil; assert(Z.limit() == 5)
        ''')

    def test_random_profession_and_trait_mutations_execute(self):
        self.check('''
            local seen = {}
            for i=1,5 do assert(Z.roll(S)); seen[S.profession] = true; assert(S.checked and #S.chosen > 0) end
            local n=0; for _ in pairs(seen) do n=n+1 end; assert(n > 1)
        ''')

    def test_sources_and_translations(self):
        for path in LUA.rglob('*.lua'):
            self.lua.execute('assert(loadstring(...))', path.read_text(encoding='utf-8'))
        for name in ('IG_UI.json', 'Sandbox.json'):
            en, ko = [json.loads((LUA / 'shared/Translate' / locale / name).read_text(encoding='utf-8'))
                      for locale in ('EN', 'KO')]
            self.assertEqual(en.keys(), ko.keys())
            for key in en:
                self.assertEqual(re.findall(r'%[1-4]', en[key]), re.findall(r'%[1-4]', ko[key]))


if __name__ == '__main__':
    unittest.main()
