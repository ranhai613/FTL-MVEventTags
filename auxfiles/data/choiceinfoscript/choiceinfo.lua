---@generic T
---@param cvec vector<T>
---@return fun(): T?, integer?, integer?
local vter_with_i_n = function (cvec)
	local i = -1
	local n = cvec:size()
	return function()
		i = i + 1
		if i < n then return cvec[i], i, n end
	end
end

local get_INFO_parser = function (full)
	return function (text)
		text = text:sub(7, -8)
		local name = text:match('%[NAME%].-%[/NAME%]')
		if name == nil then
			return ''
		end
		name = name:sub(7, -8)
		local value = Hyperspace.metaVariables['choiceInfo_event_'..name]
		if (value == 1) or full then
			if name == 'storageCheck' and Hyperspace.ships.player:HasEquipment('SALVAGE_CHECK') == 1 then
				return '\n  [style[color:00E0E0]]Storage Check(Salvage!)[[/style]]'
			end
			return '\n  '..text:gsub('%[NAME%].-%[/NAME%]', '')
		else
			return ''
		end
	end
end

local get_FightINFO_parser = function (full)
	return function (text)
		local is_worthShowing = false
		local info_parser = get_INFO_parser(full)
		text = text:sub(12, -13)
		text = text:gsub('%[INFO%].-%[/INFO%]', function (info)
			info = info_parser(info)
			if info ~= '' then
				is_worthShowing = true
			end
			return info:gsub('\n  ', ' ')
		end)
		if is_worthShowing then
			return '\n  '..text
		else
			return ''
		end
	end
end

local parse = function (text, full)
	text = text:gsub('%[FightINFO%].-%[/FightINFO%]', get_FightINFO_parser(full))
	text = text:gsub('%[INFO%].-%[/INFO%]', get_INFO_parser(full))
	return text
end

local trim_original_text = function (text)
	local _, i1 = text:find('%[FightINFO%]')
	local _, i2 = text:find('%[INFO%]')
	if i1 and i2 then
		if i1 < i2 then
			return text:sub(i1 - 10)
		else
			return text:sub(i2 - 5)
		end
	elseif i1 then
		return text:sub(i1 - 10)
	elseif i2 then
		return text:sub(i2 - 5)
	else
		return ''
	end
end

local storedTexts = {}
script.on_internal_event(Defines.InternalEvents.POST_CREATE_CHOICEBOX, function(choiceBox, event)
	storedTexts = {}
	local Choices = choiceBox:GetChoices()
	local fullInfo = '--------[Full Info]--------'
    for choice, i, n in vter_with_i_n(Choices) do
		local original_text = choice.text
        choice.text = parse(original_text, false)
		storedTexts[i] = parse(trim_original_text(original_text), true)
		fullInfo = fullInfo..'\n\n'..tostring(i + 1)..'. '..parse(original_text, true)
		if ((n - i) == 1) and (Hyperspace.metaVariables['choiceInfo_bottom_fullInfo'] == 1) then
			choice.text = choice.text..string.rep('\n', 15)..fullInfo
		end
    end
end)

script.on_render_event(Defines.RenderEvents.CHOICE_BOX, function(choiceBox) end, function(choiceBox)
	if Hyperspace.metaVariables['choiceInfo_hover_fullInfo'] ~= 1 then
		return
	end

	local potentialChoice = choiceBox.potentialChoice
	if potentialChoice > -1 then
		local text = storedTexts[potentialChoice]
		if text then
			Hyperspace.Mouse.tooltip = #Hyperspace.Mouse.tooltip > 0 and Hyperspace.Mouse.tooltip.."\n" or ""
			Hyperspace.Mouse.tooltip = Hyperspace.Mouse.tooltip..text
			Hyperspace.Mouse:InstantTooltip()
		end
	end
end)