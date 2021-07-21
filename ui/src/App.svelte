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
    import { Router, Route } from 'svelte-routing'
    import Home from './Home.svelte'
    import TodoList from './TodoList.svelte'

    export let url = ''
</script>

<Router {url}>
    <div>
        <Route path="/"><Home /></Route>
        <Route path="todo/:id" let:params>
            <TodoList id={params.id} />
        </Route>
    </div>
</Router>
