<script>
    import H1 from './H1.svelte'
    import SubHeader from './SubHeader.svelte'
    export let header
    export let subheader
</script>

<div class="flex items-center gap-4 p-0">
    <H1 text={header} />
    <SubHeader text={subheader} />
</div>
