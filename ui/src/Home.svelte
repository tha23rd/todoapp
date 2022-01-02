<style global lang="postcss">
    h1 {
        font-variant: small-caps;
        text-transform: lowercase;
    }
    button {
        font-variant: small-caps;
    }
</style>

<script>
    import { push, pop, replace } from 'svelte-spa-router'
    import ListHistory from './components/ListHistory.svelte'
    import { base_uri } from './constants'
    async function onClick() {
        // generate a new todo list
        //navigate user to /todo/:id
        const res = await fetch(`${base_uri}/todolist`, { method: 'POST' })
        const body = await res.json()
        const todo_id = body.id
        saveListInLocalStorage(todo_id)
        console.log(body)
        push(`/todo/${todo_id}`)
    }

    function saveListInLocalStorage(listId) {
        let lists = localStorage.getItem('lists')
        if (!lists) {
            lists = {}
        } else {
            lists = JSON.parse(lists)
        }

        lists[listId] = { name: 'my new todolist', createdAt: Date.now() }

        localStorage.setItem('lists', JSON.stringify(lists))
    }
</script>

<main class="container mx-auto sm:flex flex content-center h-screen">
    <div class="m-auto flex-row">
        <div class="flex flex-col md:flex-row">
            <h1 class="text-4xl text-blackish self-center m-6">welcome</h1>
            <button
                class="rounded-none border-blackish border-1 text-xl py-1 px-4 self-center mr-0 mb-8 md:mr-6 md:mb-0"
                on:click|once={onClick}
            >
                create new todo
            </button>
        </div>
        <div>
            <ListHistory />
        </div>
    </div>
</main>
