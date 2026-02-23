// import { StatusBar } from 'expo-status-bar';
// import { StyleSheet, Text, View } from 'react-native';

// export default function App() {
//   return (
//     <View style={styles.container}>
//       <Text>Open up App.js to start working on your app!app</Text>
//       <StatusBar style="auto" />
//     </View>
//   );
// }

// const styles = StyleSheet.create({
//   container: {
//     flex: 1,
//     backgroundColor: '#fff',
//     alignItems: 'center',
//     justifyContent: 'center',
//   },
// });

// App.js
import 'react-native-gesture-handler';
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';

// Importamos las vistas (las crearemos a continuación)
import LoginVista from './src/vistas/LoginVista';
import RegistroVista from './src/vistas/RegistroVista';
import PrincipalVista from './src/vistas/PrincipalVista';
// import MainVista from './src/vistas/MainVista';

const Stack = createStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator 
        initialRouteName="Login"
        screenOptions={{
          headerStyle: { backgroundColor: '#2ecc71' },
          headerTintColor: '#fff',
        }}
      >
        <Stack.Screen 
          name="Login" 
          component={LoginVista} 
          options={{ headerShown: false }} 
        />
        <Stack.Screen 
          name="Registro" 
          component={RegistroVista} 
          options={{ title: 'Crear cuenta' }}
        />
        <Stack.Screen 
          name="Main" 
          component={PrincipalVista} 
          options={{ title: 'Gestora App', headerLeft: null }} // headerLeft: null oculta el botón atrás tras loguear
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}