<style global lang="postcss">
    @tailwind base;
    @tailwind components;
    @tailwind utilities;
</style>

<script>
    import { Router, Route } from 'svelte-routing'
    import Home from './Home.svelte'
    import TodoList from './TodoList.svelte'

    export let url = ''
</script>

<svelte:head>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
        href="https://fonts.googleapis.com/css2?family=Roboto:wght@300&display=swap"
        rel="stylesheet"
    />
</svelte:head>

<body class="h-screen bg-whiteish">
    <Router {url}>
        <div>
            <Route path="/"><Home /></Route>
            <Route path="todo/:id" let:params>
                <TodoList id={params.id} />
            </Route>
        </div>
    </Router>
</body>
