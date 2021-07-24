<script>
    export let text
</script>

<span
    contenteditable="true"
    bind:innerHTML={text}
    class="md:text-5xl text-2xl font-light text-blackish self-center my-auto uppercase"
    >{text}</span
>
