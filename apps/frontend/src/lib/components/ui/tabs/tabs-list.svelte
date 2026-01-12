<script lang="ts">
	import { Tabs as TabsPrimitive } from "bits-ui";
	import { cn } from "$lib/utils";

	type $$Props = TabsPrimitive.ListProps;

	let className: $$Props["class"] = undefined;
	export { className as class };
</script>

<TabsPrimitive.List
	class={cn(
		"inline-flex h-10 items-center justify-center rounded-lg bg-white/5 p-1 text-slate-400 border border-white/10",
		className
	)}
	{...$$restProps}
>
	<slot />
</TabsPrimitive.List>
