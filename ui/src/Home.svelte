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
    import {push, pop, replace} from 'svelte-spa-router'
    import { base_uri } from "./constants"
    async function onClick() {
        // generate a new todo list
        //navigate user to /todo/:id
        const res = await fetch(`${base_uri}/todolist`, { method: 'POST' })
        const body = await res.json()
        const todo_id = body.id
        console.log(body)
        push(`/todo/${todo_id}`)
    }
</script>

<main class="container mx-auto sm:flex flex-col content-center">
    <div class="m-auto h-screen flex">
        <h1 class="text-4xl text-blackish self-center m-6">welcome</h1>
        <button
            class="rounded-none border-blackish border-1 text-xl py-1 px-4 self-center"
            on:click|once={onClick}
        >
            create new todo
        </button>
    </div>
</main>
