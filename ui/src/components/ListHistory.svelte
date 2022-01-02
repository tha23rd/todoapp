<style>
    .link {
        cursor: pointer;
    }
</style>

<script>
    import moment from 'moment-timezone'
    import { push } from 'svelte-spa-router'
    import { onMount } from 'svelte'

    let listKeys = []
    let lists = {}

    onMount(() => {
        lists = JSON.parse(localStorage.getItem('lists'))

        if (!lists) {
            lists = {}
        }

        listKeys = Object.keys(lists)
        listKeys.sort((a, b) => moment(lists[b].createdAt) - moment(lists[a].createdAt))
    })

    function listClick(listId) {
        push(`/todo/${listId}`)
    }
</script>

<div class="flex flex-col">
    {#each listKeys.slice(0, 10) as listId}
        <div class="flex self-center w-full">
            <a href={null} on:click={() => listClick(listId)}>
                <span class="font-normal mr-5 link">{lists[listId].name}</span></a
            >
            <div class="flex flex-1 items-center justify-end">
                <span class="lg:text-md text-sm text-grayish"
                    >{moment(lists[listId].createdAt).format('MM-DD-YYYY h:mm:ss')}</span
                >
            </div>
        </div>
    {/each}
</div>
