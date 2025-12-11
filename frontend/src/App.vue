<script setup>
// Main app component
</script>

<template>
  <el-config-provider>
    <div id="app">
      <router-view />
    </div>
  </el-config-provider>
</template>

<style>
#app {
  min-height: 100vh;
}

body {
  margin: 0;
  padding: 0;
}
</style>
