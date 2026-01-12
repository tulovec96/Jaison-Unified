<script lang="ts">
	import { cn } from "$lib/utils";
	import { badgeVariants, type Variant } from ".";
	import type { HTMLAttributes } from "svelte/elements";

	type $$Props = HTMLAttributes<HTMLDivElement> & {
		variant?: Variant;
	};

	let className: $$Props["class"] = undefined;
	export let variant: Variant = "default";
	export { className as class };
</script>

<div class={cn(badgeVariants({ variant }), className)} {...$$restProps}>
	<slot />
</div>
