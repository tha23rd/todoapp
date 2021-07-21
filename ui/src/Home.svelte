<script>
    import { navigate } from 'svelte-routing'
    async function onClick() {
        // generate a new todo list
        //navigate user to /todo/:id
        const res = await fetch('http://localhost:8000/todolist/', { method: 'POST' })
        const body = await res.json()
        const todo_id = body.id
        console.log(body)
        navigate(`todo/${todo_id}`)
    }
</script>

<main>
    <h1>Welcome to the todo app >:)</h1>
    <p>Click the button below to create a new shareable todo list</p>
    <button on:click|once={onClick}> Create New Todo </button>
</main>
