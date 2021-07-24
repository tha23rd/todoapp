<style global lang="postcss">
    input:checked + div {
    }
    input:checked + div svg {
        @apply block;
    }
    .thin-border {
        border-width: 1px;
    }
    .rounded-custom {
        border-radius: 3px;
    }
    .strike {
        text-decoration: line-through;
    }
</style>

<script>
    export let params
    import { io } from 'socket.io-client'
    import HeaderBar from './components/HeaderBar.svelte'
    import moment from 'moment-timezone'
    import { base_uri, ws_base_uri } from './constants'

    let new_item = ''
    let todolist = { items: [] }
    let list_name = 'My New List'

    async function connectWS() {
        const res = await fetch(`${base_uri}/todolist/${params.id}`)
        const json = await res.json()
        todolist = json
        list_name = todolist.name
        todolist.updated_date = `Last Update: ${moment(new Date(todolist.updated_date))
            .tz('America/New_York')
            .fromNow()}`
        const socket = io(ws_base_uri, {
            path: '/ws/socket.io',
            query: { roomName: params.id }
        })

        socket.on('message', function (message) {
            messages = messages.concat(message)
        })
        socket.on('todo_list_change', function (change) {
            const new_val = change.new_val
            todolist = new_val
            list_name = todolist.name
            todolist.updated_date = `Last Update: ${moment(
                new Date(todolist.updated_date)
            )
                .tz('America/New_York')
                .fromNow()}`
            console.log(change)
        })
    }

    $: {
        connectWS(params.id)
    }

    $: {
        console.log(list_name)
        debounce(() => changeListName())
    }

    function changeListName() {
        console.log('Calling@@')
        fetch(`${base_uri}/todolist/${params.id}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: list_name,
                path: 'rename_list'
            })
        })
    }
    let timer
    const debounce = v => {
        clearTimeout(timer)
        timer = setTimeout(() => {
            v()
        }, 750)
    }

    async function onAddToList() {
        const res = await fetch(`${base_uri}/todolist/${params.id}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name: new_item })
        })
        // console.log(res)
        console.log(`adding new item! ${new_item}`)
        new_item = ''
    }
    const onKeyPress = e => {
        if (e.charCode === 13) onAddToList()
    }
    async function onCheck(item) {
        await fetch(`${base_uri}/todolist/${params.id}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                is_complete: !item.is_complete,
                id: item.id,
                path: 'complete_item'
            })
        })
    }
    async function handleDelete(item) {
        const result = await fetch(`${base_uri}/todolist/${params.id}`, {
            method: 'DELETE'
        })
    }
</script>

<main>
    <div class="xl:mx-72 md:my-20 space-y-5">
        <HeaderBar bind:header={list_name} subheader={todolist.updated_date || 'test'} />
        <div>
            <input
                on:keypress={onKeyPress}
                bind:value={new_item}
                placeholder="add item..."
                class="w-full font-light text-xl border focus:outline-none bg-white text-blackish py-2 pl-3 pr-3 rounded-custom border-grayish"
                type="text"
                name="todo_item"
                id="todo_item"
            />
        </div>
        <div class="flex flex-col">
            {#each todolist.items as item}
                <div class="flex">
                    <input
                        bind:checked={item.is_complete}
                        on:click={() => onCheck(item)}
                        class="opacity-0 absolute h-8 w-8 self-center"
                        type="checkbox"
                    />
                    <div
                        class:border-greenish={item.is_complete}
                        class="bg-white thin-border rounded-full w-8 h-8 flex flex-shrink-0 justify-center items-center mr-6 self-center border-grayish "
                    >
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            class:text-greenish={item.is_complete}
                            class="fill-current hidden pointer-events-none text-grayish"
                            viewBox="0 0 512 512"
                            ><title>Checkmark</title><path
                                fill="none"
                                stroke="currentColor"
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="32"
                                d="M416 128L192 384l-96-96"
                            /></svg
                        >
                    </div>
                    <span
                        class:strike={item.is_complete}
                        class="text-2xl font-normal self-center">{item.name}</span
                    >
                    <button
                        type="button"
                        class="w-16 h-16 items-center bg-whiteish inline-flex ml-auto self-center border-none"
                    >
                        <!-- <svg class="w-6 h-6 fill-current" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="none" d="M15.584 10.001L13.998 8.417 5.903 16.512 5.374 18.626 7.488 18.097z"/><path d="M4.03,15.758l-1,4c-0.086,0.341,0.015,0.701,0.263,0.949C3.482,20.896,3.738,21,4,21c0.081,0,0.162-0.01,0.242-0.03l4-1 c0.176-0.044,0.337-0.135,0.465-0.263l8.292-8.292l1.294,1.292l1.414-1.414l-1.294-1.292L21,7.414 c0.378-0.378,0.586-0.88,0.586-1.414S21.378,4.964,21,4.586L19.414,3c-0.756-0.756-2.072-0.756-2.828,0l-2.589,2.589l-1.298-1.296 l-1.414,1.414l1.298,1.296l-8.29,8.29C4.165,15.421,4.074,15.582,4.03,15.758z M5.903,16.512l8.095-8.095l1.586,1.584 l-8.096,8.096l-2.114,0.529L5.903,16.512z"/></svg> -->
                        <!-- <svg
                            xmlns="http://www.w3.org/2000/svg"
                            class="ionicon w-10 h-10 fill-current text-grayish ml-auto"
                            viewBox="0 0 512 512"
                            ><title>Close Circle</title><path
                                d="M448 256c0-106-86-192-192-192S64 150 64 256s86 192 192 192 192-86 192-192z"
                                fill="none"
                                stroke="currentColor"
                                stroke-miterlimit="10"
                                stroke-width="32"
                            /><path
                                fill="none"
                                stroke="currentColor"
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                stroke-width="32"
                                d="M320 320L192 192M192 320l128-128"
                            /></svg
                        > -->
                        <svg
                            class="w-8 h-8 ml-auto"
                            viewBox="0 0 27 27"
                            fill="none"
                            xmlns="http://www.w3.org/2000/svg"
                        >
                            <path
                                d="M18.8033 8.19669L13.5 13.5M13.5 13.5L8.19667 18.8033M13.5 13.5L18.8033 18.8033M13.5 13.5L8.19667 8.19669M26 13.5C26 20.4036 20.4036 26 13.5 26C6.59644 26 1 20.4036 1 13.5C1 6.59644 6.59644 1 13.5 1C20.4036 1 26 6.59644 26 13.5Z"
                                stroke="#975460"
                            />
                        </svg>
                    </button>
                </div>
            {/each}
        </div>
    </div>
</main>
