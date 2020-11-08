<template>
    <div>
        <h1>Hi {{user.firstName}}!</h1>
        <p>You're logged in with Vue + Vuex & JWT!!</p>
        <h3>Users from secure api end point:</h3>
        <em v-if="projects.loading">Loading projects...</em>
        <span v-if="projects.error" class="text-danger">ERROR: {{projects.error}}</span>
        <ul v-if="projects.projects">
            <li v-for="project in projects.projects" :key="project.id">
                {{project.id + ' ' + project.name}}
            </li>
        </ul>
        <p>
            <router-link to="/login">Logout</router-link>
        </p>
    </div>
</template>

<script>
export default {
    computed: {
        user () {
            return this.$store.state.authentication.user;
        },
        projects () {
            return this.$store.state.projects.all;
        }
    },
    created () {
        this.$store.dispatch('projects/getAll');
    }
};
</script>
