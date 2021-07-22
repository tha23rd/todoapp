<style>
    main {
        text-align: center;
        padding: 1em;
        max-width: 240px;
        margin: 0 auto;
    }

    h1 {
        color: #ff3e00;
        text-transform: uppercase;
        font-size: 4em;
        font-weight: 100;
    }

    @media (min-width: 640px) {
        main {
            max-width: none;
        }
    }
</style>

<script>
    export let id
    import { io } from 'socket.io-client'
    import { onMount } from 'svelte'
    import HeaderBar from './components/HeaderBar.svelte'
    import SubHeader from './components/SubHeader.svelte'
    const socket = io('ws://localhost:8000', {
        path: '/ws/socket.io',
        query: { roomName: id }
    })
    let messages = []
    let todolist = { items: [] }
    onMount(async () => {
        socket.on('message', function (message) {
            messages = messages.concat(message)
        })
        socket.on('todo_list_change', function (change) {
            const new_val = change.new_val
            todolist = new_val
            console.log(change)
        })
    })
    console.log('here')
</script>

<main>
    <div class="m-6">
        <HeaderBar header={todolist.name || 'New List'} SubHeader={'test'} />
        <div id="chatWindow">
            <ul id="messages">
                {#each todolist.items as item}
                    <li>{item.name}</li>
                {/each}
            </ul>
        </div>
    </div>
</main>
