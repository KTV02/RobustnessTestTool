<template>
  <div>
    <h1>RobustnessTool</h1>
    <Gui />
  </div>
</template>

<script>
import Gui from "./components/Gui.vue";

export default {
  name: "App",
  components: {
    Gui,
  },
};
</script>

<style>
h1 {
  color: #333;
  font-size: 24px;
  margin-bottom: 20px;
}
</style>