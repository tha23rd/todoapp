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
    import { io } from "socket.io-client";
    const socket = io("ws://localhost:8000", {path: '/ws/socket.io', query: {roomName: "ad509ce8-daee-4084-b5d0-df3f0c15e398"}});
    export let messages = [];

    socket.on('message', function(message) {       
        messages = messages.concat(message);
    });
    socket.on('todo_list_change', function(change) {       
        console.log(change)
    });
    export let name
</script>

<main>
    <h1>Hello {name}!</h1>
    <p>
        Visit the <a href="https://svelte.dev/tutorial">Svelte tutorial</a> to learn how to
        build Svelte apps.
    </p>
    <div id="chatWindow">
        <ul id="messages">
            {#each messages as message}
            <li>{message.message}</li>
            {/each}
        </ul>
    </div>
</main>
