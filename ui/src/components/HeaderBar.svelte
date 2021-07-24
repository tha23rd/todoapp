<script>
    import H1 from './H1.svelte'
    import SubHeader from './SubHeader.svelte'
    export let header
    export let subheader
</script>

<div class="flex items-center gap-4 p-0 md:flex-row flex-col">
    <H1 bind:text={header} />
    <SubHeader text={subheader} />
</div>
