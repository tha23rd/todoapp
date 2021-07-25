<style global lang="postcss">
    @tailwind base;
    @tailwind components;
    @tailwind utilities;
</style>

<script>
    import Router from 'svelte-spa-router'
    import Home from './Home.svelte'
    import TodoList from './TodoList.svelte'

    const routes = {
        // Exact path
        '/': Home,

        // Using named parameters, with last being optional
        '/todo/:id': TodoList
    }
</script>

<svelte:head>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
        href="https://fonts.googleapis.com/css2?family=Roboto:wght@300&display=swap"
        rel="stylesheet"
    />
    <link
        href="https://fonts.googleapis.com/css2?family=Roboto:wght@400&display=swap"
        rel="stylesheet"
    />
    <style>
        body {
            background: #f3f6f9;
        }
    </style>
</svelte:head>

<body class="">
    <Router {routes} />
</body>
