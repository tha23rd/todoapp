<style>
    /* main {
        text-align: center;
        padding: 1em;
        max-width: 240px;
        margin: 0 auto;
    } */

    @media (min-width: 640px) {
        main {
            max-width: none;
        }
    }
</style>

<script>
    export let params
    import { io } from 'socket.io-client'
    import { onMount } from 'svelte'
    import HeaderBar from "./components/HeaderBar.svelte"
    import moment from "moment-timezone"
    const socket = io('ws://localhost:8000', {
        path: '/ws/socket.io',
        query: { roomName: params.id }
    })
    let new_item = ""
    let todolist = { items: [] }
    onMount(async () => {
        socket.on('message', function (message) {
            messages = messages.concat(message)
        })
        socket.on('todo_list_change', function (change) {
            const new_val = change.new_val
            todolist = new_val
            todolist.updated_date = `Last Update: ${moment(new Date(todolist.updated_date)).tz('America/New_York').fromNow()}`
            console.log(change)
        })
    })
    async function onAddToList() {
        const res = await fetch(`http://localhost:8000/todolist/${params.id}/${new_item}`, { method: 'POST' })
        console.log(res)
        console.log(`adding new item! ${new_item}`)
        new_item = ""
    }
    const onKeyPress = e => {
        if (e.charCode === 13) onAddToList();
    };
</script>

<main>
    <div class="mx-72 my-20 space-y-5">
        <HeaderBar header={todolist.name || "New List"} subheader={todolist.updated_date || "test"}/>
        <div>
            <input on:keypress={onKeyPress} bind:value={new_item} placeholder="add item..." class="font-light text-xl border focus:outline-none bg-white text-blackish py-2 pl-3 pr-3 rounded-sm" type="text" name="todo_item" id="todo_item">
        </div>
        <div class="flex flex-col" >
            {#each todolist.items as item}
                <div class="flex">
                    <span class="text-2xl font-normal">{item.name}</span>
                    <input class="ml-auto" type="checkbox">
                </div>
            {/each}
        </div>
    </div>
</main>
