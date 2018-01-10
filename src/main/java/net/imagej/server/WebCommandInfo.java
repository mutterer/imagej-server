package net.imagej.server;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

import org.scijava.command.CommandInfo;
import org.scijava.command.CommandModule;
import org.scijava.command.CommandModuleItem;
import org.scijava.module.ModuleItem;

import net.imagej.server.WebCommandModuleItem;

public class WebCommandInfo extends CommandInfo {
	
	private final CommandModule relatedCommandModule;
	
	public WebCommandInfo(CommandInfo commandInfo, CommandModule commandModule) {
		super(commandInfo);
		relatedCommandModule = commandModule;
	}
	
	public Iterable<ModuleItem<?>> inputs() {
		
		final List<WebCommandModuleItem<?>> checkedInputs = new ArrayList<>();
		for (final ModuleItem<?> input : super.inputs()) {
			if (input.getClass().equals(CommandModuleItem.class)) {
				WebCommandModuleItem<?> webCommandModuleItem = new WebCommandModuleItem<>(this, (CommandModuleItem<?>)input);
				final String name = input.getName();

				// Include resolved status in the JSON feed.
				// This is handy for judiciously overwriting already-resolved inputs,
				// particularly the "active image" inputs, which will be reported as
				// resolved, but not necessarily match what's selected on the client side.
				webCommandModuleItem.isResolved = relatedCommandModule.isInputResolved(name);

				// Include startingValue in the JSON feed.
				// Useful for populating the dialog!
				webCommandModuleItem.startingValue = relatedCommandModule.getInput(name);
				
				checkedInputs.add(webCommandModuleItem);					
			}
		}
		
		return Collections.unmodifiableList(checkedInputs);
	}
}